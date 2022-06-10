# Winning Horse
## *Proyecto Final de Ciclo DAW 2020-2022*

El proyecto despliega una *API Rest* que sirve los datos necesarios a la aplicación desarrollada en el *Proyecto Fin de Ciclo de Desarrollo de Aplicaciones Web*, elaborado por el alumno *José Pablo Vázquez García*, y cuya función consiste en la gestión de carreras y apuestas ecuestres. Además, da acceso a los usuarios administradores a un panel con el que podrán realizar los cambios a la base de datos que consideren pertinentes.

En el proyecto se ha hecho uso de diversas extensiones del framework **Flask**, como pueden ser *SQLAlchemy*, *Flask-marshmallow*, *Flask-CORS* o *Flask-Praetorian*.

La aplicación consta, además, de una *interfaz frontend* desarrollada en JavaScript bajo el framework **React** que da acceso a los clientes a los datos, a través de peticiones *HTTP*. Esta aplicación puede descargarse desde el siguiente repositorio de **GitHub**:

[Enlace a la aplicación Cliente](https://github.com/JPabloV85/Proyecto_Final_DAW_Front.git)

### Arranque del proyecto con Docker

1. Arrancar la herramienta **Docker**
2. Descargar el archivo *docker-compose.yml*.
3. Abrir un terminal y ubicarse en el directorio donde se haya almacenado el archivo.
4. Ejecutar el comando **docker compose up**.

### Alternativa de arranque

1. Descargar o clonar la API Rest.
2. Descargar o clonar la aplicación cliente.
3. En un terminal ubicado en el directorio del proyecto *frontend*, ejecutar el comando **npm install** (instalación de dependencias).
4. Una vez completado el paso anterior, ejecutar el comando **npm run start**
5. En un terminal diferente ubicado en el directorio de la API Rest, ejecutar el comando **flask run**

### Acceso a la interfaz del cliente

- Abrir [http://localhost:3000](http://localhost:3000) para visualizar en el navegador.
- Las credenciales para la conexión con una cuenta de cliente de prueba son:
    - Username: pablo
    - Password: alberti

### Acceso a la interfaz del servidor

- Abrir [http://localhost:5000](http://localhost:5000) para visualizar en el navegador.
- Las credenciales para la conexión con una cuenta de administrador de prueba son:
    - Username: pedro
    - Password: alberti