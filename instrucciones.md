# CUSTOMER SERVICE INSTRUCTIONS

Hola equipo!!!! Les explico maso como funciona este microservicio:

1. **Propósito**: Este microservicio se encarga de gestionar a los clientes, incluyendo la creación, actualización, eliminación y consulta de información de clientes. Está repartido en 4 funciones lambda principales.

2. **Funciones Lambda**:
   - `createCustomer`: Crea un nuevo cliente en la base de datos.
     - Endpoint: `POST /tenant/{tenantID}/customers`
   - `loginCustomer`: Permite a un cliente iniciar sesión en el sistema.
     - Endpoint: `POST /tenant/{tenantID}/customers/login`
   - `updateCustomer`: Actualiza la información de un cliente existente.
     - Endpoint: `PUT /tenant/{tenantID}/customers/{customerID}`
   - `deleteCustomer`: Elimina un cliente de la base de datos.
     - Endpoint: `PATCH /tenant/{tenantID}/customers/{customerID}/deactivate`
   - `getCustomer`: Recupera la información de un cliente específico.
     - Endpoint: `GET /tenant/{tenantID}/customers/{customerID}`
   - `getMe`: Recupera la información del cliente autenticado.
     - Endpoint: `GET /tenant/{tenantID}/customers/me`

3. **Base de Datos**: Utiliza DynamoDB para almacenar la información de los clientes. Cada cliente tiene atributos como `customerID`, `name`, `email`, `password`, `createdAt`, y `updatedAt`.

Está escrito en python pq ez.