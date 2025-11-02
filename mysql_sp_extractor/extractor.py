import mysql.connector
import os
from datetime import datetime
from typing import List, Tuple, Optional, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StoredProcedureExtractor:
    """Extrae procedimientos almacenados de MemSQL/SingleStore"""
    
    def __init__(self, host: str, port: int, user: str, password: str, 
                 database: str, output_dir: str = "./stored_procedures"):
        """
        Inicializa el extractor
        
        Args:
            host: Hostname de la base de datos
            port: Puerto de conexión
            user: Usuario de la base de datos
            password: Contraseña
            database: Nombre de la base de datos
            output_dir: Directorio de salida para los archivos
        """
        self.config = {
            'host': host,
            'port': port,
            'user': user,
            'password': password,
            'database': database
        }
        self.output_dir = output_dir
        self.conn = None
    
    def connect(self) -> bool:
        """Establece conexión con la base de datos"""
        try:
            self.conn = mysql.connector.connect(**self.config)
            logger.info(f"✓ Conectado a {self.config['host']}:{self.config['port']}")
            return True
        except mysql.connector.Error as err:
            logger.error(f"✗ Error de conexión: {err}")
            return False
    
    def disconnect(self):
        """Cierra la conexión"""
        if self.conn and self.conn.is_connected():
            self.conn.close()
            logger.info("✓ Conexión cerrada")
    
    def create_output_directory(self):
        """Crea el directorio de salida si no existe"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            logger.info(f"✓ Directorio creado: {self.output_dir}")
        else:
            logger.info(f"✓ Usando directorio: {self.output_dir}")
    
    def get_routines(self, routine_type: str = 'PROCEDURE') -> List[Tuple[str, str]]:
        """
        Obtiene la lista de procedimientos o funciones
        
        Args:
            routine_type: 'PROCEDURE' o 'FUNCTION'
        
        Returns:
            Lista de tuplas (nombre, tipo)
        """
        cursor = self.conn.cursor()
        query = """
            SELECT ROUTINE_NAME, ROUTINE_TYPE
            FROM INFORMATION_SCHEMA.ROUTINES
            WHERE ROUTINE_SCHEMA = %s
            AND ROUTINE_TYPE = %s
            ORDER BY ROUTINE_NAME
        """
        cursor.execute(query, (self.config['database'], routine_type))
        routines = cursor.fetchall()
        cursor.close()
        return routines
    
    def get_routine_definition(self, routine_name: str, 
                               routine_type: str = 'PROCEDURE') -> Optional[str]:
        """
        Obtiene la definición de un procedimiento o función
        
        Args:
            routine_name: Nombre del procedimiento/función
            routine_type: 'PROCEDURE' o 'FUNCTION'
        
        Returns:
            Definición SQL o None si hay error
        """
        cursor = self.conn.cursor()
        command = "SHOW CREATE PROCEDURE" if routine_type == 'PROCEDURE' else "SHOW CREATE FUNCTION"
        query = f"{command} `{routine_name}`"
        
        try:
            cursor.execute(query)
            result = cursor.fetchone()
            if result and len(result) >= 3:
                return result[2]
            return None
        except mysql.connector.Error as err:
            logger.error(f"  ✗ Error obteniendo {routine_name}: {err}")
            return None
        finally:
            cursor.close()
    
    def save_routine(self, routine_name: str, definition: str, 
                    routine_type: str = 'PROCEDURE') -> bool:
        """
        Guarda el procedimiento en un archivo
        
        Args:
            routine_name: Nombre del procedimiento
            definition: Definición SQL
            routine_type: 'PROCEDURE' o 'FUNCTION'
        
        Returns:
            True si se guardó exitosamente
        """
        suffix = "_FUNC" if routine_type == 'FUNCTION' else ""
        filename = os.path.join(self.output_dir, f"{routine_name}{suffix}.sql")
        
        # Encabezado del archivo
        header = f"""-- ============================================
-- {routine_type}: {routine_name}
-- Base de datos: {self.config['database']}
-- ============================================

"""
        
        # Contenido completo con DROP y DELIMITER
        drop_command = "DROP PROCEDURE" if routine_type == 'PROCEDURE' else "DROP FUNCTION"
        content = f"{header}{drop_command} IF EXISTS `{routine_name}`;\n\nDELIMITER $$\n\n{definition}$$\n\nDELIMITER ;\n"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            logger.error(f"  ✗ Error guardando {filename}: {e}")
            return False
    
    def extract_all(self, include_functions: bool = True) -> Dict[str, int]:
        """
        Extrae todos los procedimientos y opcionalmente funciones
        
        Args:
            include_functions: Si debe extraer funciones también
        
        Returns:
            Diccionario con contadores de éxito
        """
        if not self.conn or not self.conn.is_connected():
            logger.error("No hay conexión establecida")
            return {'procedures': 0, 'functions': 0}
        
        self.create_output_directory()
        
        results = {'procedures': 0, 'functions': 0}
        
        # Extraer procedimientos
        logger.info(f"🔍 Buscando procedimientos en '{self.config['database']}'...")
        procedures = self.get_routines('PROCEDURE')
        
        if procedures:
            logger.info(f"✓ Encontrados {len(procedures)} procedimientos\n")
            logger.info("📦 Extrayendo procedimientos...")
            
            for name, routine_type in procedures:
                definition = self.get_routine_definition(name, 'PROCEDURE')
                if definition and self.save_routine(name, definition, 'PROCEDURE'):
                    logger.info(f"  ✓ {name}")
                    results['procedures'] += 1
        else:
            logger.warning("✗ No se encontraron procedimientos")
        
        # Extraer funciones
        if include_functions:
            functions = self.get_routines('FUNCTION')
            
            if functions:
                logger.info(f"\n📦 Extrayendo {len(functions)} funciones...")
                
                for name, routine_type in functions:
                    definition = self.get_routine_definition(name, 'FUNCTION')
                    if definition and self.save_routine(name, definition, 'FUNCTION'):
                        logger.info(f"  ✓ {name}")
                        results['functions'] += 1
        
        return results