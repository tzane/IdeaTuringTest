from app import db
from models import ArgumentPost, User

db.create_all()

# insert
db.session.add(ArgumentPost("$15 Federal Minimum Wage", False, False, "DON\'T TREAD ON ME!", "OBAMA\'S NEW SOCIALISM IS ALL ABOUT GOVERNMENT HANDOUTS TO THE POOR AND LAZY", 1))
db.session.add(ArgumentPost("$15 Federal Minimum Wage", False, False, "The minimum wage is relatively high-risk to vulnerable workers and is poor a policy choice relative to other politically feasible options.", "Although the employment effects are empirically mixed, we should not risk pricing vulnerable low-skilled workers out of the labor market and passing on higher costs to consumers in these industries (most of whom are themselves low-income consumers). There are other politically feasible policy options which are low-risk to workers and directly target poverty. These policy options include direct cash subsidies (e.g. basic income or negative income tax) and refundable tax credits (e.g. earned income tax credits).", 2))
db.session.add(ArgumentPost("$15 Federal Minimum Wage", False, True, "The minimum wage hurts small businesses more than large corporations.", "Small businesses are the lifeblood of the American economy and increases in the minimum wage will destroy these jobs. Why stop at $15 an hour? Why not $100 an hour?! Why not just pay everyone in cocaine and unicorns?", 3))
db.session.add(User("Natalie", "nat@natalie.com", "password"))
db.session.add(User("Tyler", "ty@tyler.com", "password"))
db.session.add(User("Kevin", "kev@kevin.com", "password"))


#commit
db.session.commit()