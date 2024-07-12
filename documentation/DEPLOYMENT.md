# Deployment Guide for AiryBites

This guide provides detailed steps to deploy the AiryBites project, which is built using Flask, MongoDB, and Jinja2 templating, and hosted on Heroku. The project is developed and managed using GitPod and GitHub.

## Prerequisites

Ensure you have the following prerequisites installed and set up:

- A GitHub account
- A Heroku account
- Git installed on your local machine
- A MongoDB database (e.g., MongoDB Atlas)
- GitPod workspace (optional but recommended for development)

## Step 1: Clone the Repository

First, clone the AiryBites repository from GitHub to your local machine:

```sh
git clone https://github.com/yourusername/airybite.git
cd airybite
```
## Step 2: Set Up Environment Variables
Create a file named env.py in the root directory of the project and add the following environment variables:

```sh
import os

os.environ["MONGO_DBNAME"] = "your_mongodb_name"
os.environ["MONGO_URI"] = "your_mongodb_uri"
os.environ["SECRET_KEY"] = "your_secret_key"
```
Make sure to replace your_mongodb_name, your_mongodb_uri, and your_secret_key with your actual MongoDB database name, URI, and a secret key for Flask sessions, respectively.

### Setting Up MongoDB
If you are using MongoDB Atlas, follow these steps:

1. **Create an Account:** Sign up for an account at MongoDB Atlas.
2. **Create a Cluster:** Follow the instructions to create a new cluster.
3. **Database Access:** Set up a database user with the necessary permissions.
4. **Network Access:** Allow access from your IP address or set to allow access from anywhere (less secure).
5. **Get Connection String:** Retrieve your MongoDB connection string (URI). It will look something like this:
```
mongodb+srv://<username>:<password>@cluster0.mongodb.net/<dbname>?retryWrites=true&w=majority
```
6. **Update Environment Variables:** Replace <username>, <password>, and <dbname> in the connection string and use it as your_mongodb_uri in env.py.

### Adding env.py to .gitignore
To ensure that your sensitive environment variables are not tracked by Git, add env.py to your .gitignore file:

1. Open or create a file named .gitignore in the root directory of your project.
2. Add the following line to .gitignore:
```env.py```
3. Save and close the .gitignore file.



## Step 3: Set Up GitPod (Optional)
To develop using GitPod, you need to open your repository in GitPod.
Alternatively, you can use VS Code or any other IDE.

```
gitpod.io/#https://github.com/yourusername/airybites
```

## Step 4: Install Dependencies
Install the required Python packages using pip:
```sh
pip install -r requirements.txt
```
## Step 5: Run the Application Locally
To test the application locally, run the Flask development server:
```sh
python3 app.py
```
The application should now be running at http://localhost:5000.

## Step 6: Prepare for Heroku Deployment
Create a Procfile in the root directory with the following content:
```sh
web: python app.py
```
Ensure your requirements.txt is up to date:
```sh
pip freeze > requirements.txt
```

## Step 7: Deploy to Heroku
Login to Heroku and create a new application:
```sh
heroku login
heroku create airybite
```
Set up the environment variables on Heroku:
```sh
heroku config:set MONGO_DBNAME=your_mongodb_name
heroku config:set MONGO_URI=your_mongodb_uri
heroku config:set SECRET_KEY=your_secret_key
```
Replace your_mongodb_name, your_mongodb_uri, and your_secret_key with the actual values.

## Step 8: Push to Heroku
Initialise a Git repository (if not already done), add Heroku remote, and deploy:
```sh
git init
heroku git:remote -a airybite
git add .
git commit -m "Initial commit"
git push heroku main
```

## Step 9: Access Your Application
After deploying, you can access your application at [heroku](https://www.heroku.com/home)
Your link will look somthing like this: https://airybites-app-9649332aa316.herokuapp.com/

## Conclusion
You have successfully deployed the AiryBites project to Heroku. For any changes, commit them to your GitHub repository and push to Heroku to update your application.

For any issues or further customization, refer to the [Heroku Flask documentation](https://devcenter.heroku.com/articles/getting-started-with-python).

*Happy coding!*