import os

project_structure = {
    "FcMara": {
        "app": {
            "__init__.py": "",
            "config.py": "",
            "models": {
                "__init__.py": "",
                "user.py": "",
                "player.py": "",
                "event.py": "",
                "game.py": "",
                "statistics.py": "",
                "trophy.py": "",
            },
            "routes": {
                "__init__.py": "",
                "auth.py": "",
                "admin.py": "",
                "public.py": "",
            },
            "forms": {
                "__init__.py": "",
                "login.py": "",
                "player.py": "",
                "event.py": "",
                "game.py": "",
            },
            "static": {
                "css": {},
                "js": {},
                "img": {},
            },
            "templates": {
                "base.html": "",
                "auth": {
                    "login.html": "",
                },
                "admin": {
                    "dashboard.html": "",
                    "players.html": "",
                    "events.html": "",
                    "games.html": "",
                },
                "public": {
                    "index.html": "",
                    "league.html": "",
                    "tournaments.html": "",
                    "statistics.html": "",
                    "trophies.html": "",
                },
            },
            "utils": {
                "__init__.py": "",
            },
        },
        "migrations": {},
        "requirements.txt": "",
        "run.py": "",
    }
}

def create_structure(base_path, structure):
    for name, content in structure.items():
        path = os.path.join(base_path, name)
        if isinstance(content, dict):
            os.makedirs(path, exist_ok=True)
            create_structure(path, content)
        else:
            with open(path, 'w') as f:
                f.write(content)

if __name__ == "__main__":
    create_structure(".", project_structure)
    print("✅ Project structure created successfully!")
