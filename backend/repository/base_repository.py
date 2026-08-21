# backend/repository/base_repository.py
"""
Base repository with generic CRUD operations.
All specific repositories inherit from this class.
"""

import logging
from typing import TypeVar, Generic, Type, Optional, List, Dict, Any
from backend.config.database import db
from backend.utils.exceptions import NotFoundError, DatabaseError

logger = logging.getLogger(__name__)

T = TypeVar('T')  # Type variable for model class


class BaseRepository(Generic[T]):
    """
    Generic repository providing common CRUD operations.
    
    Args:
        model_class: The model class (e.g., Product, User)
        table_name: The database table name
        id_field: The primary key field name (default: 'id')
    """
    
    def __init__(self, model_class: Type[T], table_name: str, id_field: str = 'id'):
        self.model_class = model_class
        self.table_name = table_name
        self.id_field = id_field
    
    def _to_dict(self, obj: T) -> Dict[str, Any]:
        """
        Converts a model object to a dictionary.
        Override this if your model has a to_dict() method.
        """
        if hasattr(obj, 'to_dict'):
            return obj.to_dict()
        # Fallback: return object's __dict__ (excluding private attributes)
        return {k: v for k, v in obj.__dict__.items() if not k.startswith('_')}
    
    def _from_dict(self, data: Dict[str, Any]) -> T:
        """
        Creates a model instance from a dictionary.
        Override this if your model constructor requires specific handling.
        """
        return self.model_class(**data)
    
    def get_all(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[T]:
        """
        Retrieves all records from the table.
        
        Args:
            limit: Maximum number of records to return
            offset: Number of records to skip
        
        Returns:
            List[T]: List of model instances
        """
        query = f"SELECT * FROM {self.table_name} ORDER BY {self.id_field}"
        params = []
        
        if limit is not None:
            query += " LIMIT %s"
            params.append(limit)
        if offset is not None:
            query += " OFFSET %s"
            params.append(offset)
        
        try:
            with db.get_cursor(dict_cursor=True) as cur:
                cur.execute(query, tuple(params))
                rows = cur.fetchall()
                return [self._from_dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error fetching all from {self.table_name}: {str(e)}")
            raise DatabaseError(f"Failed to fetch records: {str(e)}")
    
    def get_by_id(self, record_id: int) -> Optional[T]:
        """
        Retrieves a single record by its primary key.
        
        Args:
            record_id: Primary key value
        
        Returns:
            Optional[T]: Model instance or None if not found
        
        Raises:
            NotFoundError: If record not found
        """
        query = f"SELECT * FROM {self.table_name} WHERE {self.id_field} = %s"
        
        try:
            with db.get_cursor(dict_cursor=True) as cur:
                cur.execute(query, (record_id,))
                row = cur.fetchone()
                if not row:
                    raise NotFoundError(
                        resource=self.model_class.__name__,
                        identifier=record_id
                    )
                return self._from_dict(row)
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error fetching by id from {self.table_name}: {str(e)}")
            raise DatabaseError(f"Failed to fetch record: {str(e)}")
    
    def get_by_field(self, field: str, value: Any) -> List[T]:
        """
        Retrieves records matching a specific field value.
        
        Args:
            field: Column name
            value: Value to match
        
        Returns:
            List[T]: List of matching model instances
        """
        query = f"SELECT * FROM {self.table_name} WHERE {field} = %s"
        
        try:
            with db.get_cursor(dict_cursor=True) as cur:
                cur.execute(query, (value,))
                rows = cur.fetchall()
                return [self._from_dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error fetching by field from {self.table_name}: {str(e)}")
            raise DatabaseError(f"Failed to fetch records: {str(e)}")
    
    def get_by_fields(self, filters: Dict[str, Any]) -> List[T]:
        """
        Retrieves records matching multiple field values.
        
        Args:
            filters: Dictionary of field:value pairs
        
        Returns:
            List[T]: List of matching model instances
        """
        if not filters:
            return self.get_all()
        
        conditions = []
        params = []
        for field, value in filters.items():
            conditions.append(f"{field} = %s")
            params.append(value)
        
        where_clause = " AND ".join(conditions)
        query = f"SELECT * FROM {self.table_name} WHERE {where_clause}"
        
        try:
            with db.get_cursor(dict_cursor=True) as cur:
                cur.execute(query, tuple(params))
                rows = cur.fetchall()
                return [self._from_dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error fetching by fields from {self.table_name}: {str(e)}")
            raise DatabaseError(f"Failed to fetch records: {str(e)}")
    
    def create(self, data: Dict[str, Any]) -> T:
        """
        Inserts a new record into the table.
        
        Args:
            data: Dictionary of column:value pairs (excluding id if auto-generated)
        
        Returns:
            T: The created model instance with generated ID
        """
        # Remove id if present (will be auto-generated)
        data_copy = data.copy()
        data_copy.pop(self.id_field, None)
        
        columns = list(data_copy.keys())
        placeholders = [f"%s"] * len(columns)
        values = list(data_copy.values())
        
        query = f"""
            INSERT INTO {self.table_name} ({', '.join(columns)})
            VALUES ({', '.join(placeholders)})
            RETURNING {self.id_field}
        """
        
        try:
            new_id = None
            with db.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, values)
                    new_id = cur.fetchone()[0]
            return self.get_by_id(new_id)
        except DatabaseError:
            raise
        except Exception as e:
            logger.error(f"Error creating record in {self.table_name}: {str(e)}")
            raise DatabaseError(f"Failed to create record: {str(e)}")
    
    def update(self, record_id: int, data: Dict[str, Any]) -> T:
        """
        Updates an existing record.
        
        Args:
            record_id: Primary key value
            data: Dictionary of column:value pairs to update
        
        Returns:
            T: The updated model instance
        
        Raises:
            NotFoundError: If record not found
        """
        # First check if record exists
        self.get_by_id(record_id)
        
        # Remove id from data if present
        data_copy = data.copy()
        data_copy.pop(self.id_field, None)
        
        if not data_copy:
            # Nothing to update, return existing record
            return self.get_by_id(record_id)
        
        set_clause = ", ".join([f"{k} = %s" for k in data_copy.keys()])
        values = list(data_copy.values())
        values.append(record_id)
        
        query = f"""
            UPDATE {self.table_name}
            SET {set_clause}
            WHERE {self.id_field} = %s
            RETURNING {self.id_field}
        """
        
        try:
            with db.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, values)
                    updated_id = cur.fetchone()
                    if not updated_id:
                        raise NotFoundError(
                            resource=self.model_class.__name__,
                            identifier=record_id
                        )
            return self.get_by_id(record_id)
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error updating record in {self.table_name}: {str(e)}")
            raise DatabaseError(f"Failed to update record: {str(e)}")
    
    def delete(self, record_id: int) -> bool:
        """
        Deletes a record by its primary key.
        
        Args:
            record_id: Primary key value
        
        Returns:
            bool: True if deleted, False if not found
        
        Raises:
            NotFoundError: If record not found
        """
        # First check if record exists
        self.get_by_id(record_id)
        
        query = f"DELETE FROM {self.table_name} WHERE {self.id_field} = %s"
        
        try:
            with db.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (record_id,))
                    affected = cur.rowcount
                    # get_connection commits automatically on exit
                    if affected == 0:
                        raise NotFoundError(
                            resource=self.model_class.__name__,
                            identifier=record_id
                        )
                    return True
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error deleting record from {self.table_name}: {str(e)}")
            raise DatabaseError(f"Failed to delete record: {str(e)}")
    
    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Counts records in the table, optionally with filters.
        
        Args:
            filters: Optional dictionary of field:value pairs to filter
        
        Returns:
            int: Number of records
        """
        if filters:
            conditions = []
            params = []
            for field, value in filters.items():
                conditions.append(f"{field} = %s")
                params.append(value)
            where_clause = " AND ".join(conditions)
            query = f"SELECT COUNT(*) FROM {self.table_name} WHERE {where_clause}"
        else:
            query = f"SELECT COUNT(*) FROM {self.table_name}"
            params = []
        
        try:
            with db.get_cursor() as cur:
                cur.execute(query, tuple(params))
                return cur.fetchone()[0]
        except Exception as e:
            logger.error(f"Error counting records in {self.table_name}: {str(e)}")
            raise DatabaseError(f"Failed to count records: {str(e)}")
    
    def exists(self, record_id: int) -> bool:
        """
        Checks if a record exists by its primary key.
        
        Args:
            record_id: Primary key value
        
        Returns:
            bool: True if exists, False otherwise
        """
        try:
            self.get_by_id(record_id)
            return True
        except NotFoundError:
            return False
    
    def execute_raw_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """
        Executes a raw SQL query and returns results.
        
        Args:
            query: SQL query string
            params: Query parameters
        
        Returns:
            List[Dict]: Query results as dictionaries
        """
        try:
            with db.get_cursor(dict_cursor=True) as cur:
                cur.execute(query, params)
                return cur.fetchall()
        except Exception as e:
            logger.error(f"Error executing raw query: {str(e)}")
            raise DatabaseError(f"Failed to execute query: {str(e)}")