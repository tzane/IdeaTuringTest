from app import db, bcrypt
from models import ArgumentPost, User

db.create_all()

# insert
db.session.add(ArgumentPost("The federal government should impose a national $15/hr minimum wage.", False, False, "DON\'T TREAD ON ME!", "OBAMA\'S NEW SOCIALISM IS ALL ABOUT GOVERNMENT HANDOUTS TO THE POOR AND LAZY", 1))
db.session.add(ArgumentPost("The federal government should impose a national $15/hr minimum wage.", False, False, "The minimum wage is relatively high-risk to vulnerable workers and is poor a policy choice relative to other politically feasible options.", "Although the employment effects are empirically mixed, we should not risk pricing vulnerable low-skilled workers out of the labor market and passing on higher costs to consumers in these industries (most of whom are themselves low-income consumers). There are other politically feasible policy options which are low-risk to workers and directly target poverty. These policy options include direct cash subsidies (e.g. basic income or negative income tax) and refundable tax credits (e.g. earned income tax credits).", 2))
db.session.add(ArgumentPost("The federal government should impose a national $15/hr minimum wage.", False, True, "The minimum wage hurts small businesses more than large corporations.", "Small businesses are the lifeblood of the American economy and increases in the minimum wage will destroy these jobs. Why stop at $15 an hour? Why not $100 an hour?! Why not just pay everyone in cocaine and unicorns?", 3))
db.session.add(ArgumentPost("The federal government should impose a national $15/hr minimum wage.", False, True, "The minimum wage hurts society\'s most disadvantaged people looking for work even if it doesn\'t increase overall unemployment.", "If I\'m an employer who is now forced to hire at a higher wage then I will expect greater productivity to off-set the additional cost. Therefore, I will be more likely to hire an older experienced worker who came out of retirement to work for the higher wage instead of a troubled minority youth who is in desperate need of work.", 4))     
db.session.add(ArgumentPost("The federal government should impose a national $15/hr minimum wage.", True, False, "WE ARE THE 1%!", "AND WE WILL NOT TOLERATE THE SYSTEMATIC OPPRESSION AND EXTORTION OF WORKERS BY GREEDY CORPORATIONS.", 1))
db.session.add(ArgumentPost("The federal government should impose a national $15/hr minimum wage.", True, False, "The minimum wage ensures that employers invest in their employees and is overall good for the economy.", "The industry demand for labor is much more inelastic than most economists think. A $15/hr minimum wage will not cause significant levels unemployment and, therefore, helps redistribute profits from investors and corporate executives to the workers without significant unemployment risks. What's more, labor has a greater propensity to consume with their income which further stimulates overall aggregate demand.", 2))
db.session.add(ArgumentPost("The federal government should impose a national $15/hr minimum wage.", True, True, "Everyone deserves a living wage!", "The share of income to labor has fallen steadily since the decline of the welfare state in the late 1960s.", 3))
db.session.add(ArgumentPost("The federal government should impose a national $15/hr minimum wage.", True, True, "Everyone that puts in a full day\'s worth of hard work deserves a modest standard of living.", "There's enough millionaires and, even billionaires, out there to ensure the rest of us are well taken care of.", 4))

db.session.add(User("Natalie", "nat@natalie.com", "password"))
db.session.add(User("Tyler", "ty@tyler.com", "password"))
db.session.add(User("Kevin", "kev@kevin.com", "password"))
db.session.add(User("David","dav@david.com", "test"))

db.session.add(Vote(2, 8, 1))
db.session.add(Vote(3, 5, 1))
db.session.add(Vote(4, 9, 1))
db.session.add(Vote(1, 1, 2))
db.session.add(Vote(3, 4, 2))
db.session.add(Vote(4, 10, 2))
#commit
db.session.commit()