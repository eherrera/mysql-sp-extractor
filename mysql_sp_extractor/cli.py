import argparse
import sys
from pathlib import Path
from dotenv import load_dotenv
import os
from .extractor import StoredProcedureExtractor


def load_config_from_env(env_file: str = '.env') -> dict:
    """Carga configuración desde archivo .env"""
    if not Path(env_file).exists():
        print(f"❌ Archivo {env_file} no encontrado")
        print("\nCrea un archivo .env con el siguiente formato:")
        print("""
DB_HOST=tu_host
DB_PORT=3306
DB_USER=tu_usuario
DB_PASS=tu_password
DB_NAME=tu_base_de_datos
OUTPUT_DIR=./stored_procedures
""")
        sys.exit(1)
    
    load_dotenv(env_file)
    
    config = {
        'host': os.getenv('DB_HOST'),
        'port': int(os.getenv('DB_PORT', 3306)),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASS'),
        'database': os.getenv('DB_NAME'),
        'output_dir': os.getenv('OUTPUT_DIR', './stored_procedures')
    }
    
    # Validar campos requeridos
    required = ['host', 'user', 'password', 'database']
    missing = [k for k in required if not config[k]]
    
    if missing:
        print(f"❌ Faltan variables requeridas en {env_file}: {', '.join(missing)}")
        sys.exit(1)
    
    return config


def main():
    """Función principal del CLI"""
    parser = argparse.ArgumentParser(
        description='Extrae procedimientos almacenados de MemSQL/SingleStore',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  # Usar archivo .env por defecto
  memsql-sp-extractor
  
  # Especificar archivo .env personalizado
  memsql-sp-extractor --env .env.production
  
  # Proporcionar credenciales por línea de comandos
  memsql-sp-extractor --host localhost --user admin --database mydb
  
  # Excluir funciones
  memsql-sp-extractor --no-functions
        """
    )
    
    parser.add_argument('--env', default='.env', help='Archivo .env con configuración')
    parser.add_argument('--host', help='Hostname de la base de datos')
    parser.add_argument('--port', type=int, default=3306, help='Puerto (default: 3306)')
    parser.add_argument('--user', help='Usuario de la base de datos')
    parser.add_argument('--password', help='Contraseña')
    parser.add_argument('--database', help='Nombre de la base de datos')
    parser.add_argument('--output-dir', default='./stored_procedures', 
                       help='Directorio de salida (default: ./stored_procedures)')
    parser.add_argument('--no-functions', action='store_true',
                       help='No extraer funciones, solo procedimientos')
    parser.add_argument('--version', action='version', version='%(prog)s 0.1.0')
    
    args = parser.parse_args()
    
    # Determinar fuente de configuración
    if args.host and args.user and args.database:
        # Usar argumentos de línea de comandos
        config = {
            'host': args.host,
            'port': args.port,
            'user': args.user,
            'password': args.password or input('Password: '),
            'database': args.database,
            'output_dir': args.output_dir
        }
    else:
        # Usar archivo .env
        config = load_config_from_env(args.env)
    
    print("=" * 60)
    print("  EXTRACTOR DE PROCEDIMIENTOS ALMACENADOS")
    print("  MemSQL/SingleStore/Mysql")
    print("=" * 60)
    print()
    
    # Crear extractor y ejecutar
    extractor = StoredProcedureExtractor(**config)
    
    if not extractor.connect():
        sys.exit(1)
    
    try:
        results = extractor.extract_all(include_functions=not args.no_functions)
        
        print("\n" + "=" * 60)
        print(f"✓ Procedimientos extraídos: {results['procedures']}")
        if not args.no_functions:
            print(f"✓ Funciones extraídas: {results['functions']}")
        print(f"✓ Archivos guardados en: {os.path.abspath(config['output_dir'])}")
        print("=" * 60)
        
    finally:
        extractor.disconnect()


if __name__ == '__main__':
    main()
