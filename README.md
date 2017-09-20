# TingoID-API

Repositorio de la aplicación TingoID donde se encuentra la API de interacción de la aplicación con la base de datos y los servidores externos

## Instalación

Para realizar la instalación de este repositorio se necesita tener un entorno de desarrollo que contemple los requerimientos de requirements.txt

### Entorno de desarrollo virtual (_virtualenv_)

Para crear un entorno de desarrollo virtual o encapsulado se necesita de los siguientes requermientos:

Instalación de _python3_:

```
(mac)$ brew install python3
(linux)$ apt-get install python3-dev
(win)$ plz no!
```

Con esto también se instalará _pip3_ un gestor de paquetes de _python_ el cual permite instalar los requerimientos del repositorio. Adicional a esto necesitamos generar un entorno de desarrollo virtual encapsulado, para eso vamos a utilizar el gestor de paquetes para instalar el paquete _virtualenv_ el cual nos va a permitir instanciar un entorno encapsulado.

```
$ pip3 install virtualenv
```

Ahora que ya tenemos todos los requisitos cumplidos, se procede a generar el entorno virtual, para esto nos ubicamos en la carpeta principal del repositorio.

```
$ cd path/to/repo/
$ virtualenv venv
```

Con esto se creará una carpeta llamada tingo, en la cual se instalarán todos los paquetes de manera encapsulada. Para iniciar la encapsulación se debe realizar __(Este proceso de debe realizar cada vez que se abre una nueva terminal)__:

```
$ source venv/bin/activate
(venv) $
```

Con esto ya podemos instalar los requerimientos del repositorio:

```
(venv) $ pip install -r requirements.txt
```

## Desarrollo

Para el desarrollo de esta aplicación se utiliza el framework de desarrollo _Django_:

[Documentación Django](https://docs.djangoproject.com/)

## Levantar el servidor

Para realizar el levantamiento del servidor se debe ejecutar el siguiente comando:

```
(venv) $ ./manage.py runserver
```

Si se necesita realizar un levantamiento del servidor que sea visible por parte de otros dispositivos, se debe copiar la _IP_ del computador en la red actual en los parametros del comando _runserver_ y explicitar el puerto de conexión:

```
(venv) $ ./manage.py runserver IP:Port
ej: (venv) $ ./manage.py runserver 192.168.1.117:8000
```

## Desarrollo

Para el desarrollo de esta aplicación se deben utilizar _branchs_ que salgan desde `master` y luego realizar un _pull request_, para esto se debe subir al repositorio la _branch_ utilizada y luego crear un _pull request_ en la interfaz web de GitHub

## Como crear Pull Request

Para crear un pull request se debe trabajar en una rama alterna a _master_ con el comando:

```
$ git checkout -b nombre_rama
```

Se crea una nueva rama que va a salir desde la rama actual (`master`). En esta rama se deben realizar todos los cambios que se quieran y luego se deben añadir con el comando:

```
$ git add -A (-A sirve para añadir todo lo modificado)
```

Luego se debe commitear

```
$ git commit -a -m "Comentario del commit" (-a es para añadir todo y -m es para añadir comentario)
```

Una vez listos los cambios se debe subir la rama de trabajo con el comando:

```
$ git push origin nombre_rama
```

Luego de esto en la ventana principal del repositorio en el navegador, se habilitará una opción de generar un _pull request_
