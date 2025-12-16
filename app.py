from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os 
from logging.config import dictConfig

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'DEBUG',
        'handlers': ['wsgi']
    }
})


app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Character(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    # Personnal info
    last_name = db.Column(db.String(200), nullable=False, default='Doe')
    name = db.Column(db.String(200), nullable=False, default='John')
    age = db.Column(db.Integer, nullable=False, default=20)
    race = db.Column(db.String(200), nullable=False, default='Humain')
    social_class = db.Column(db.String(200), nullable=False, default='Plébien')
    talent = db.Column(db.String(200), nullable=False, default='Aucun')
    adventurer_rank = db.Column(db.String(200), nullable=False, default='Aucun')

    # Physical stats
    strength = db.Column(db.String(200), nullable=False, default='E')
    speed = db.Column(db.String(200), nullable=False, default='E')
    resistance = db.Column(db.String(200), nullable=False, default='E')
    sword_style = db.Column(db.String(200), nullable=False, default='Aucun')
    smith_rank = db.Column(db.String(200), nullable=False, default='/')
    alchemy_rank = db.Column(db.String(200), nullable=False, default='/')

    # Magic stats
    mana_reserve = db.Column(db.String(200), nullable=False, default='Très faible')
    mana_zone = db.Column(db.String(200), nullable=False, default='/')
    magic_mastery = db.Column(db.String(2000), nullable=False, default='/')

    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    # Relation
    skills = db.relationship('Skill', backref='owner', lazy='dynamic', cascade="all, delete-orphan")
    items = db.relationship('Item', backref='owner', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Character {self.id} : {self.name}>'


class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, default=". . .")
    content = db.Column(db.String(20000), nullable=False, default=". . .")
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    

    character_id = db.Column(db.Integer, db.ForeignKey('character.id'), nullable=False)
    
    def __repr__(self):
        return f'<Skill {self.id} : {self.name}>'
    
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, default=". . .")
    content = db.Column(db.String(2000), nullable=False, default=". . .")
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    character_id = db.Column(db.Integer, db.ForeignKey('character.id'), nullable=False)

    def __repr__(self):
        return f'<Item {self.id} : {self.name}>'

with app.app_context():
    db.create_all()


# --- ROUTES FOR CHARACTERS ---
@app.route("/", methods=["GET"])
def index():
    characters = Character.query.order_by(Character.date_created.desc()).all()
    return render_template("index.html", characters = characters)

@app.route('/create', methods=["POST", "GET"])
def create():
    if request.method == 'POST':

        character_last_name = request.form['last_name'].strip()
        character_name = request.form['name'].strip()
        
        try:
            character_age = int(request.form['age']) 
        except ValueError:
            return 'L\'âge doit être un nombre valide.', 400
            
        character_race = request.form['race'].strip()
        character_social_class = request.form['social_class'].strip()
        character_talent = request.form['talent'].strip()
        character_adventurer_rank = request.form['adventurer_rank'].strip()

        character_strength = request.form['strength'].strip()
        character_speed = request.form['speed'].strip()
        character_resistance = request.form['resistance'].strip()
        character_sword_style = request.form['sword_style'].strip()
        character_smith_rank = request.form['smith_rank'].strip() # Correction .strip
        character_alchemy_rank = request.form['alchemy_rank'].strip()

        character_mana_reserve = request.form['mana_reserve'].strip()
        character_mana_zone = request.form['mana_zone'].strip()
        character_magic_mastery = request.form['magic_mastery'].strip()
        
        new_character = Character(
            name=character_name,
            last_name=character_last_name,
            age=character_age,
            race=character_race,
            social_class=character_social_class,
            talent=character_talent,
            adventurer_rank=character_adventurer_rank,

            strength=character_strength,
            speed=character_speed,
            resistance=character_resistance,
            sword_style=character_sword_style,
            smith_rank=character_smith_rank,
            alchemy_rank=character_alchemy_rank,

            mana_reserve=character_mana_reserve,
            mana_zone=character_mana_zone,
            magic_mastery=character_magic_mastery,
        )

        try:
            db.session.add(new_character)
            app.logger.info(f"Personnage ajouté: {new_character}")
            db.session.commit()
            return redirect(url_for('index'))
        except Exception as e:
            app.logger.error(f"Erreur d'ajout: {e}")
            return 'Une erreur est survenue lors de l\'ajout du personnage.', 500
    
    else:
        return render_template('create.html') 
    
@app.route("/delete/<int:id>", methods=["POST"]) 
def delete(id):
    character_to_delete = Character.query.get_or_404(id)
    try:
        db.session.delete(character_to_delete)
        app.logger.info(f"Personnage supprimé: {character_to_delete}")
        db.session.commit()
        return redirect(url_for('index'))
    except:
        app.logger.error(f"Erreur lors de la suppression du personnage: {character_to_delete}")
        return 'Une erreur est survenue lors de la suppression du personnage.', 500

    
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    character = Character.query.get_or_404(id) 

    if request.method == 'POST':

        new_last_name = request.form['last_name'].strip()
        new_name = request.form['name'].strip()
        
        try:
            new_age = int(request.form['age']) 
        except ValueError:
            app.logger.error("Âge invalide fourni lors de la mise à jour.")
            return 'L\'âge doit être un nombre valide.', 400
            
        new_race = request.form['race'].strip()
        new_social_class = request.form['social_class'].strip()
        new_talent = request.form['talent'].strip()
        new_adventurer_rank = request.form['adventurer_rank'].strip()

        new_strength = request.form['strength'].strip()
        new_speed = request.form['speed'].strip()
        new_resistance = request.form['resistance'].strip()
        new_sword_style = request.form['sword_style'].strip()
        new_smith_rank = request.form['smith_rank'].strip()
        new_alchemy_rank = request.form['alchemy_rank'].strip()

        new_mana_reserve = request.form['mana_reserve'].strip()
        new_mana_zone = request.form['mana_zone'].strip()
        new_magic_mastery = request.form['magic_mastery'].strip()
        
        try:
            character.last_name = new_last_name
            character.name = new_name 
            character.age = new_age
            character.race = new_race
            character.social_class = new_social_class
            character.talent = new_talent
            character.adventurer_rank = new_adventurer_rank

            character.strength = new_strength
            character.speed = new_speed
            character.resistance = new_resistance
            character.sword_style = new_sword_style
            character.smith_rank = new_smith_rank
            character.alchemy_rank = new_alchemy_rank

            character.mana_reserve = new_mana_reserve
            character.mana_zone = new_mana_zone
            character.magic_mastery = new_magic_mastery
            app.logger.info(f"Personnage mis à jour: {character}")
            db.session.commit()
            return redirect(url_for('index'))
        
        except Exception as e:
            app.logger.error(f"Erreur de mise à jour: {e}")
            return 'Une erreur est survenue lors de la mise à jour de la tâche.', 500
    
    else:
        return render_template('update.html', character=character)

@app.route('/character/<int:id>')
def details(id):
    character = Character.query.get_or_404(id)
    return render_template('details.html', character = character)


# --- ROUTES FOR SKILLS ---


@app.route('/character/<int:char_id>/skill', methods=['GET'])
def skills(char_id):
    character = Character.query.get_or_404(char_id)
    skills = character.skills.order_by(Skill.date_created.desc()).all() 
    return render_template('skill.html', skills=skills, character=character)

@app.route('/character/<int:char_id>/skill/create_skill', methods=["POST", "GET"])
def create_skill(char_id):
    character = Character.query.get_or_404(char_id)
    if request.method == 'POST':
        skill_name = request.form['name'].strip()
        skill_content = request.form['content'].strip()
        
        new_skill = Skill(
            name=skill_name,
            content=skill_content,
            character_id=char_id 
        )
    
        try:
            db.session.add(new_skill)
            app.logger.info(f"Compétence ajoutée: {new_skill}")
            db.session.commit()

            return redirect(url_for('skills', char_id=char_id)) 
        except Exception as e:
            app.logger.error(f"Erreur d'ajout de skill: {e}")
            return 'Une erreur est survenue lors de l\'ajout de la compétence.', 500
    else:
        return render_template('create_skill.html', character=character)

@app.route("/character/<int:char_id>/skill/delete_skill/<int:skill_id>", methods=["POST"])
def delete_skill(char_id, skill_id):
    deleted_skill = Skill.query.get_or_404(skill_id)
    try:
        db.session.delete(deleted_skill)
        app.logger.info(f"Compétence supprimée: {deleted_skill}")
        db.session.commit()

        return redirect(url_for('skills', char_id=char_id)) 
    except:
        app.logger.error(f"Erreur lors de la suppression de la compétence: {deleted_skill}")
        return 'Une erreur est survenue lors de la suppression de la compétence.', 500

@app.route('/character/<int:char_id>/skill/update_skill/<int:skill_id>', methods=['GET', 'POST'])
def update_skill(char_id, skill_id):
    character = Character.query.get_or_404(char_id)
    skill = Skill.query.get_or_404(skill_id)
    
    if request.method == 'POST':

        new_name = request.form['name'].strip()
        new_content = request.form['content'].strip()
        
        try:
            skill.name = new_name
            skill.content = new_content
            app.logger.info(f"Compétence mise à jour: {skill}")
            db.session.commit()
            return redirect(url_for('skills', char_id=char_id))
        except Exception as e:
            app.logger.error(f"Erreur de mise à jour: {e}")
            return 'Une erreur est survenue lors de la mise à jour de la compétence.', 500
    
    else:
        return render_template('update_skill.html', skill=skill, character = character)


@app.route('/character/<int:char_id>/skill/<int:skill_id>')
def details_skill(char_id, skill_id):
    skill = Skill.query.get_or_404(skill_id)
    character = Character.query.get_or_404(char_id)

    if skill.character_id != character.id:
        app.logger.error(f"Incohérence: la compétence {skill.id} n'appartient pas au personnage {character.id}")
        return "Compétence non trouvée pour ce personnage.", 404
        
    return render_template('details_skill.html', skill = skill, character = character)


# --- ROUTES FOR INVENTORY ---

@app.route('/character/<int:char_id>/inventory', methods=['GET'])
def inventory(char_id):
    character = Character.query.get_or_404(char_id)
    items = character.items.order_by(Item.date_created.desc()).all() 
    return render_template('inventory.html', items=items, character=character)

@app.route('/character/<int:char_id>/inventory/create_item', methods=["POST", "GET"])
def create_item(char_id):
    character = Character.query.get_or_404(char_id)
    if request.method == 'POST':
        item_name = request.form['name'].strip()
        item_content = request.form['content'].strip()
        
        new_item = Item(
            name=item_name,
            content=item_content,
            character_id=char_id
        )
    
        try:
            db.session.add(new_item)
            app.logger.info(f"Item ajouté: {new_item}")
            db.session.commit()
            
            return redirect(url_for('inventory', char_id=char_id)) 
        except Exception as e:
            app.logger.error(f"Erreur d'ajout d'item: {e}")
            return "Une erreur est survenue lors de l\'ajout de l'item.", 500
    else:
        return render_template('create_item.html', character=character)
    
@app.route('/character/<int:char_id>/inventory/update_item/<int:item_id>', methods=['GET', 'POST'])
def update_item(char_id, item_id):
    character = Character.query.get_or_404(char_id)
    item = Item.query.get_or_404(item_id)
    
    if request.method == 'POST':

        new_name = request.form['name'].strip()
        new_content = request.form['content'].strip()
        
        try:
            item.name = new_name
            item.content = new_content
            app.logger.info(f"Item mis à jour: {item}")
            db.session.commit()
            return redirect(url_for('inventory', char_id=char_id)) 
        except Exception as e:
            app.logger.error(f"Erreur de mise à jour: {e}")
            return 'Une erreur est survenue lors de la mise à jour de la compétence.', 500
    
    else:
        return render_template('update_item.html', item=item, character = character)

@app.route("/character/<int:char_id>/inventory/delete_item/<int:item_id>", methods=["POST"])
def delete_item(char_id, item_id):
    deleted_item = Item.query.get_or_404(item_id)
    try:
        db.session.delete(deleted_item)
        app.logger.info(f"Item supprimé: {deleted_item}")
        db.session.commit()
  
        return redirect(url_for('inventory', char_id=char_id)) 
    except:
        app.logger.error(f"Erreur lors de la suppression de l'item: {deleted_item}")
        return 'Une erreur est survenue lors de la suppression de la compétence.', 500

if __name__ == '__main__':
    app.run(debug=True)

@app.route("/logs", methods=["GET", "POST"])
def logs():
    return render_template("admin_logs.html")
