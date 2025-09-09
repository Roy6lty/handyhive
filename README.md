# 🛠️ Handy Hive

**Handy Hive** is a service provider platform built with **FastAPI** and **PostgreSQL + PostGIS**, designed to connect users with skilled professionals like plumbers, mechanics, electricians, and more — all in one place.

Users can search for nearby service providers, view their profiles, negotiate prices, and hire them directly through the platform.

---

## 🚀 Features

- 🔍 **Location-based search** using PostGIS spatial queries
- 🧰 **Service provider profiles** with categories and ratings
- 💬 **Negotiation system** for flexible pricing
- 📍 **Geospatial indexing** for fast proximity filtering
- 🐍 **FastAPI backend** for high-performance APIs
- 🗄️ **PostgreSQL + PostGIS** for robust data and spatial support

---

## 🧱 Tech Stack

| Layer      | Technology               |
| ---------- | ------------------------ |
| Backend    | Python + FastAPI         |
| Database   | PostgreSQL + PostGIS     |
| ORM        | SQLAlchemy + GeoAlchemy2 |
| Auth       | JWT (planned)            |
| Deployment | Render (or Docker)       |

---

## 📦 Installation

# Clone the repository

git clone https://github.com/Roy6lty/handyhive.git
cd handyhive

# Create and activate a virtual environment

python -m venv venv
source venv/bin/activate

# Install dependencies

pip install -r requirements.txt
