# MySQL Stored Procedure Extractor

[![PyPI version](https://badge.fury.io/py/mysql-sp-extractor.svg)](https://badge.fury.io/py/mysql-sp-extractor)
[![Python Versions](https://img.shields.io/pypi/pyversions/mysql-sp-extractor.svg)](https://pypi.org/project/mysql-sp-extractor/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Herramienta de línea de comandos para extraer procedimientos almacenados y funciones de bases de datos MemSQL/SingleStore (y MySQL compatible) a archivos SQL individuales.

## Características

✅ Extrae procedimientos almacenados y funciones  
✅ Guarda cada uno en archivos SQL individuales
✅ Formato listo para re-importar (con DROP IF EXISTS)  
✅ Soporte para archivos `.env` para credenciales  
✅ CLI intuitivo con múltiples opciones  

## Instalación

```bash
pip install mysql-sp-extractor
```

## Uso Rápido

### 1. Usando archivo .env (recomendado)

Crea un archivo `.env`:

```bash
DB_HOST=localhost
DB_PORT=3306
DB_USER=admin
DB_PASS=password
DB_NAME=mi_base_datos
OUTPUT_DIR=./stored_procedures
```

Ejecuta:

```bash
mysql-sp-extractor
```

### 2. Usando argumentos de línea de comandos

```bash
mysql-sp-extractor --host localhost --user admin --database mydb --output-dir ./backup
```

### 3. Usando como librería Python

```python
from mysql_sp_extractor import StoredProcedureExtractor

extractor = StoredProcedureExtractor(
    host='localhost',
    port=3306,
    user='admin',
    password='password',
    database='mydb',
    output_dir='./sp_backup'
)

if extractor.connect():
    results = extractor.extract_all(include_functions=True)
    print(f"Extraídos: {results['procedures']} procedimientos, {results['functions']} funciones")
    extractor.disconnect()
```

## Opciones del CLI

```
mysql-sp-extractor [opciones]

Opciones:
  --env FILE              Archivo .env con configuración (default: .env)
  --host HOST             Hostname de la base de datos
  --port PORT             Puerto (default: 3306)
  --user USER             Usuario
  --password PASSWORD     Contraseña
  --database DB           Nombre de la base de datos
  --output-dir DIR        Directorio de salida (default: ./stored_procedures)
  --no-functions          No extraer funciones, solo procedimientos
  --version               Mostrar versión
  --help                  Mostrar ayuda
```

## Ejemplos

### Extraer solo procedimientos (sin funciones)

```bash
mysql-sp-extractor --no-functions
```

### Usar archivo .env personalizado

```bash
mysql-sp-extractor --env .env.production
```

### Especificar directorio de salida

```bash
mysql-sp-extractor --output-dir /backup/sp/$(date +%Y%m%d)
```

## Formato de Salida

Cada procedimiento se guarda en un archivo individual:

```
stored_procedures/
├── calcular_total.sql
├── procesar_pedido.sql
├── actualizar_inventario.sql
└── obtener_datos_FUNC.sql  (funciones tienen sufijo _FUNC)
```

Ejemplo de contenido:

```sql
-- ============================================
-- PROCEDURE: calcular_total
-- Base de datos: mydb
-- ============================================

DROP PROCEDURE IF EXISTS `calcular_total`;

DELIMITER $$

CREATE PROCEDURE `calcular_total`(IN order_id INT)
BEGIN
    -- Código del procedimiento
END$$

DELIMITER ;
```

## Compatibilidad

- MemSQL / SingleStore
- MySQL 5.7+
- MySQL 8.0+
- MariaDB 10.x

## Requisitos

- Python 3.7+
- mysql-connector-python
- python-dotenv

## Desarrollo

```bash
# Clonar repositorio
git clone https://github.com/eherrera/mysql-sp-extractor.git
cd mysql-sp-extractor

# Instalar en modo desarrollo
pip install -e ".[dev]"

# Ejecutar tests
pytest

# Formatear código
black .
```

## Licencia

MIT License - Ver archivo [LICENSE](LICENSE) para más detalles

## Contribuir

¡Las contribuciones son bienvenidas! Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Soporte

- 🐛 [Reportar bugs](https://github.com/eherrera/mysql-sp-extractor/issues)
- 💡 [Solicitar features](https://github.com/eherrera/mysql-sp-extractor/issues)
- 📖 [Documentación](https://github.com/eherrera/mysql-sp-extractor#readme)


---

⭐ Si este proyecto te fue útil, considera darle una estrella en GitHub!
