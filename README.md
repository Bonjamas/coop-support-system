# 🛠️ Coop IT Support System

Et simpelt internt ticket system udviklet som alternativ til ServiceNow, hvor man kan oprette og håndtere support tickets.

🚀 Brug lokalt:
- git clone https://github.com/Bonjamas/coop-support-system.git
- cd coop-support-system  

📦 Opret et virtual environment:
- python -m venv venv  

⚙️ Aktivér environment:
- Windows → venv\Scripts\activate  
- Mac/Linux → source venv/bin/activate  

📥 Installer dependencies:
- pip install -r requirements.txt  

🔐 Opret en `.env` fil i projektets rod:
- ENV=development
- DATABASE_URL=postgresql://coop:coop123@localhost:5432/coop_db  
- SECRET_KEY=devkey

- CLIENT_ID=<din-client-id>
- CLIENT_SECRET=<din-client-secret>
- TENANT_ID=<din-tenant-id>

- ADMIN_GROUP_ID=<din-admin-group-id>
- SUPPORT_GROUP_ID=<din-support-group-id>
- BUTIK_GROUP_ID=<din-butik-group-id> 

🐳 Databasen kører via Docker (PostgreSQL). Start den med:
- docker-compose up -d  

🛑 Stop databasen igen med:
- docker-compose down  

🔄 Hvis du ændrer database strukturen, skal databasen nulstilles:
- docker-compose down  
- docker volume rm coop-support-system_postgres_data  
- docker-compose up -d  

⚠️ Dette sletter alle data og opretter databasen på ny.

▶️ Når databasen kører, kan du starte applikationen:
- python app.py  

🌐 Åbn derefter i browser:
- http://127.0.0.1:5000  

💡 Vigtigt at vide:
- Databasen kører i Docker, mens applikationen kører lokalt i Flask  
- Der bruges ikke migrations, så ændringer i database struktur kræver reset af Docker volume  
- Det kræver de rigtige entra id oplysninger for at hjemmeside virker.