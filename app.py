import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)

# Ref 1: https://flask-pymongo.readthedocs.io/en/latest/
# Helper function to get ingredient name by id
def get_ingredient_name(ingredient_id):
    ingredient = mongo.db.ingredients.find_one({"_id": ObjectId(ingredient_id)})
    if ingredient:
        return ingredient["ing_name"]
    return "Unknown Ingredient"

# Below I registered the get_ingredient_name function as a global function in Jinja2 templates
# This allows the function to be called directly within any Jinja2 template without
# needing to pass it explicitly.
# Ref1: https://flask.palletsprojects.com/en/2.3.x/templating/
# Ref2: https://stackoverflow.com/questions/43335931/global-variables-in-flask-templates
app.jinja_env.globals.update(get_ingredient_name=get_ingredient_name)


# Route to display recipes
@app.route("/")
@app.route("/get_recipes")
def get_recipes():
    recipes = mongo.db.recipes.find()
    return render_template("index.html", recipes=recipes, get_ingredient_name=get_ingredient_name)


# Route to display registration page
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Check if password match
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            flash("Passwords do not match. Please try again.", "error")
            return redirect(url_for("register"))

        # Check if username already exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists.<br>Please choose another username.")
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        # Put new User into Session (cookie)
        session["user"] = request.form.get("username").lower()
        flash("Registration Succesful!")
        return redirect(url_for("profile", username=session["user"]))
    return render_template("register.html")


# Route to display login pge
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
         # Check if username already exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # Check if hashed password of user matches
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                flash("Welcome, {}".format(request.form.get("username")))
                return redirect(url_for("profile", username=session["user"]))
            else:
                # Password not match to user message
                flash("Incorrect Username and/or Password! <br> Please check and try again.")
                return redirect(url_for("login"))

        else:
            # User does not exsits
            flash("Incorrect Username and/or Password! <br> Please check and try again.")
            return redirect(url_for("login"))

    return render_template("login.html")


# Route to display user profile page
@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # Get username session username from the database
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    return render_template("profile.html", username=username)


# Route to remove user from session 
@app.route("/logout")
def logout():
    # Remove user session (logout)
    flash("You have logged out")
    session.pop("user")
    return redirect(url_for("login"))


# Route to add recipe to the database
@app.route("/add_recipe", methods=["GET", "POST"])
def add_recipe():
    if request.method == "POST":
        category = request.form["category_name"]
        recipe_title = request.form["recipe_title"]
        recipe_description = request.form["recipe_description"]
        cook_time = int(request.form["cook_time"])
        prep_time = int(request.form["prep_time"])
        total_time = cook_time + prep_time
        temperature = int(request.form["temperature"])
        servings = int(request.form["servings"])
        instructions = request.form["instructions"].split("\n")
        image_url = request.form["image_url"]
        tags = request.form["tags"].split(",")

        ingredient_names = request.form.getlist("ingredient_name[]")
        ingredient_quantities = request.form.getlist("ingredient_quantity[]")

        ingredient_refs = []

        for name, quantity in zip(ingredient_names, ingredient_quantities):
            ingredient = mongo.db.ingredients.find_one({"ing_name": name})  # Use "ing_name" here
            if not ingredient:
                ingredient_id = mongo.db.ingredients.insert_one({"ing_name": name}).inserted_id  # Insert new ingredient
            else:
                ingredient_id = ingredient["_id"]
            ingredient_refs.append({
                "ingredient_id": ingredient_id,
                "quantity": quantity
            })

        created_at = datetime.datetime.now()
        updated_at = datetime.datetime.now()

        recipe = {
            "recipe_title": recipe_title,
            "recipe_description": recipe_description,
            "instructions": instructions,
            "cook_time": cook_time,
            "prep_time": prep_time,
            "total_time": total_time,
            "temperature": temperature,
            "servings": servings,
            "image_url": image_url,
            "category": category,
            "tags": tags,
            "ingredients": ingredient_refs,
            "created_at": created_at,
            "updated_at": updated_at,
            "created_by": session["user"]
        }
        mongo.db.recipes.insert_one(recipe)
        flash("Recipe Successfully Added")
        return redirect(url_for("get_recipes"))

    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template("add_recipe.html", categories=categories)


# 
@app.route("/edit_recipe/<recipe_id>", methods=["GET", "POST"])
def edit_recipe(recipe_id):
    if request.method == "POST":
        category = request.form["category_name"]
        recipe_title = request.form["recipe_title"]
        recipe_description = request.form["recipe_description"]
        cook_time = int(request.form["cook_time"])
        prep_time = int(request.form["prep_time"])
        total_time = cook_time + prep_time
        temperature = int(request.form["temperature"])
        servings = int(request.form["servings"])
        instructions = request.form["instructions"].split("\n")
        image_url = request.form["image_url"]
        tags = request.form["tags"].split(",")

        ingredient_names = request.form.getlist("ingredient_name[]")
        ingredient_quantities = request.form.getlist("ingredient_quantity[]")

        ingredient_refs = []

        for name, quantity in zip(ingredient_names, ingredient_quantities):
            ingredient = mongo.db.ingredients.find_one({"ing_name": name})  # Use "ing_name" here
            if not ingredient:
                ingredient_id = mongo.db.ingredients.insert_one({"ing_name": name}).inserted_id  # Insert new ingredient
            else:
                ingredient_id = ingredient["_id"]
            ingredient_refs.append({
                "ingredient_id": ingredient_id,
                "quantity": quantity
            })

        created_at = datetime.datetime.now()
        updated_at = datetime.datetime.now()

        update = {
            "recipe_title": recipe_title,
            "recipe_description": recipe_description,
            "instructions": instructions,
            "cook_time": cook_time,
            "prep_time": prep_time,
            "total_time": total_time,
            "temperature": temperature,
            "servings": servings,
            "image_url": image_url,
            "category": category,
            "tags": tags,
            "ingredients": ingredient_refs,
            "created_at": created_at,
            "updated_at": updated_at,
            "created_by": session["user"]
        }
        mongo.db.recipes.update_one({"_id": ObjectId(recipe_id)}, {"$set": update})
        flash("Recipe Successfully Updated")
    
    recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template("edit_recipe.html", recipe=recipe, categories=categories)



if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
