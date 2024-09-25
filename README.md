# Book Lend
The Book Lend Application is a technical assessment built on a microservices architecture, aimed at streamlining the lending and management of books. It utilizes RabbitMQ as a message broker to enable communication between the two services: [admin_api](https://github.com/cgzirim/book-lend/tree/main/admin_api) and [frontend_api](https://github.com/cgzirim/book-lend/tree/main/frontend_api).

## Installation and Running

### Prerequisites 🧑‍🤝‍🧑
- Docker
- Docker Compose

### Steps to Install and Run 🚶

1. **Clone the Repository**
   ```bash
   git clone git@github.com:cgzirim/book-lend.git
   cd book-lend-app
   ```
2. **Build and Run the Application**
   ```
   docker-compose up --build
   ```
3. **Access the Application**
- Admin API: 
  - Access the API at: [http://localhost:7000](http://localhost:7000)
  - Swagger Documentation: [http://localhost:7000/docs/](http://localhost:7000/docs/)
  
- Frontend API: 
  - Access the API at: [http://localhost:8000](http://localhost:8000)
  - Swagger Documentation: [http://localhost:8000/docs/](http://localhost:8000/docs/)
  
- RabbitMQ Management: 
  - Access the management interface at: [http://localhost:15672](http://localhost:15672) 
  - Default credentials: 
    - **Username**: guest 
    - **Password**: guest

<div class="image-container">
        <img src="https://github.com/user-attachments/assets/74571c34-6199-4a19-93ce-e57e5b07ad2c" 
             alt="admin_api" 
             width="500">
        <img src="https://github.com/user-attachments/assets/74091f8e-b2cd-4737-9dcc-6d68f68b0bcc" 
             alt="frontend_api" 
             width="500">
</div>
