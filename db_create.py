from app import db, bcrypt
from models import User, Topic, Motion, Argument, Vote, ProposedTopic, ProposedTopicVote, ProposedTopicComment, ArgumentComment
import datetime
from random import randint

db.create_all()

# insert
db.session.add(User("Emily", "em@emily.com", "password"))
db.session.add(User("Tyler", "ty@tyler.com", "password"))
db.session.add(User("Kevin", "kev@kevin.com", "password"))
db.session.add(User("David","dav@david.com", "password"))
db.session.add(User("Nick","nic@nick.com", "password"))

db.session.add(Topic("Economy", "The federal government should impose a national $15/hr minimum wage.", 2, True)) 
db.session.add(Topic("International Relations", "The immediate re-militarization of NATO should be a top priority in advancing U.S. national security interests.", 5, True)) 
db.session.add(Topic("Economy", "Something something about the economy.", 2, True)) 
db.session.add(Topic("Environment", "Something something about the environment.", 5, True))
db.session.add(Topic("International Relations", "Something something about international relations.", 3, True))
db.session.add(Topic("Environment", "Something about the Kyoto Protocol.", 1, True))

db.session.add(ProposedTopic("Environment", "Something about the environment at the G8 summit.", 1))
db.session.add(ProposedTopic("International Relations", "The TPP deal will ultimately benefit everyone and should be ratified immediately.", 2))
db.session.add(ProposedTopic("Constitutional Law", "Roe vs. Wade (1973) should be overturned.", 3))

# boolean vote_value, proposed_topic.id, author_id
db.session.add(ProposedTopicVote(True, 1, 2))
db.session.add(ProposedTopicVote(False, 1, 3))
db.session.add(ProposedTopicVote(False, 1, 4))
db.session.add(ProposedTopicVote(True, 1, 5)) 
db.session.add(ProposedTopicVote(False, 2, 1))
db.session.add(ProposedTopicVote(False, 2, 3))
db.session.add(ProposedTopicVote(True, 2, 4))
db.session.add(ProposedTopicVote(True, 2, 5))
db.session.add(ProposedTopicVote(True, 3, 1))
db.session.add(ProposedTopicVote(False, 3, 4))

# comment, proposed_topic.id, author_id
db.session.add(ProposedTopicComment("Great idea! This seems pretty clear and reasonable. Let's up-vote this people!", 1, 2))
db.session.add(ProposedTopicComment("This shouldn't even be debated. Stop giving the evil 1% a platform. Hurr durr!", 2, 3))
db.session.add(ProposedTopicComment("What do you mean by everyone? That's pretty important to make clear.", 2, 5))
db.session.add(ProposedTopicComment("What about Roe vs. Wade? Can you be more specific? I'm down-voting this until you clarify.", 3, 1))

# topic_id, user_id, user_procon
db.session.add(Motion(1, 1, False))
db.session.add(Motion(1, 2, False)) 
db.session.add(Motion(1, 3, True))
db.session.add(Motion(1, 4, True))
db.session.add(Motion(1, 5, False))
db.session.add(Motion(2, 1, True))
db.session.add(Motion(2, 2, False)) 
db.session.add(Motion(2, 3, True))
db.session.add(Motion(2, 4, True))
db.session.add(Motion(2, 5, False))
db.session.add(Motion(3, 1, True))
db.session.add(Motion(3, 2, True)) 
db.session.add(Motion(3, 3, True))
db.session.add(Motion(3, 4, False))
db.session.add(Motion(3, 5, False))
db.session.add(Motion(4, 1, False))
db.session.add(Motion(4, 2, True))
db.session.add(Motion(4, 3, True))
db.session.add(Motion(4, 4, False))
db.session.add(Motion(4, 5, True))
db.session.add(Motion(6, 1, True))
db.session.add(Motion(6, 2, True)) 
db.session.add(Motion(6, 3, True))
db.session.add(Motion(6, 4, False))
db.session.add(Motion(6, 5, False))

# abstract, argument, author_id, motion_id
db.session.add(Argument(False, "DON\'T TREAD ON ME!", "OBAMA\'S NEW SOCIALISM IS ALL ABOUT GOVERNMENT HANDOUTS TO THE POOR AND LAZY", 1, 1))
db.session.add(Argument(False, "A $15/hr minimum wage is relatively high-risk to vulnerable workers and is poor a policy choice relative to other politically feasible options.", "Although the employment effects are empirically mixed, we should not risk pricing vulnerable low-skilled workers out of the labor market and passing on higher costs to consumers in these industries (most of whom are themselves low-income consumers). There are other politically feasible policy options which are low-risk to workers and directly target poverty. These policy options include direct cash subsidies (e.g. basic income or negative income tax) and refundable tax credits (e.g. earned income tax credits).", 2, 2))
db.session.add(Argument(False, "The minimum wage hurts small businesses more than large corporations.", "Small businesses are the lifeblood of the American economy and increases in the minimum wage will destroy these jobs. Why stop at $15 an hour? Why not $100 an hour?! Why not just pay everyone in cocaine and unicorns?", 3, 3))
db.session.add(Argument(False, "A $15/hr minimum wage would hurt society\'s most disadvantaged people looking for work even if it doesn\'t increase overall unemployment.", "If I\'m an employer who is now forced to hire at a higher wage then I will expect greater productivity to off-set the additional cost. Therefore, I will be more likely to hire an older experienced worker who came out of retirement to work for the higher wage instead of a troubled minority youth who is in desperate need of work.", 4, 4))     
db.session.add(Argument(False, "Just expand the earned income tax credit (EITC) instead!", "The EITC is far more effective at alleviating poverty since it's a direct cash subsidy instead of a dangerously high price floor which is what a $15/hr minimum wage is.", 5, 5))

db.session.add(Argument(False, "WAR IS NOT THE ANSWER!!", "THE UNITED STATES SHOULD STOP TRYING TO ASSERT IT\'S HEGEMONY IN THE REGION.", 1, 6))
db.session.add(Argument(False, "At this stage it is both unwise and unnecessary to provoke Putin. There are other less aggressive options.", "Western sanctions coupled with the low energry prices are crippling Russia\'s economy. This in turn is reducing domestic support.", 2, 7))
db.session.add(Argument(False, "Kevin\'s con abstract.", "Kevin\'s con argument.", 3, 8))
db.session.add(Argument(False, "David\'s con abstract.", "David\'s con argument.", 4, 9))
db.session.add(Argument(False, "Nick\'s con abstract.", "Nick\'s con argument.", 5, 10))

db.session.add(Argument(False, "Emily\'s con abstract.", "Emily\'s con abstract.", 1, 11))
db.session.add(Argument(False, "Tyler\'s con abstract", "Tyler\'s con argument.", 2, 12))
db.session.add(Argument(False, "Kevin\'s con abstract.", "Kevin\'s con argument.", 3, 13))
db.session.add(Argument(False, "David\'s con abstract.", "David\'s con argument.", 4, 14))
db.session.add(Argument(False, "Nick\'s con abstract.", "Nick\'s con argument.", 5, 15))

db.session.add(Argument(False, "Emily\'s con abstract.", "Emily\'s con abstract.", 1, 16))
db.session.add(Argument(False, "Tyler\'s con abstract", "Tyler\'s con argument.", 2, 17))
db.session.add(Argument(False, "Kevin\'s con abstract.", "Kevin\'s con argument.", 3, 18))
db.session.add(Argument(False, "David\'s con abstract.", "David\'s con argument.", 4, 19))
db.session.add(Argument(False, "Nick\'s con abstract.", "Nick\'s con argument.", 5, 20))

db.session.add(Argument(False, "Emily\'s con abstract.", "Emily\'s con abstract.", 1, 21))
db.session.add(Argument(False, "Tyler\'s con abstract", "Tyler\'s con argument.", 2, 22))
db.session.add(Argument(False, "Kevin\'s con abstract.", "Kevin\'s con argument.", 3, 23))
db.session.add(Argument(False, "David\'s con abstract.", "David\'s con argument.", 4, 24))
db.session.add(Argument(False, "Nick\'s con abstract.", "Nick\'s con argument.", 5, 25))

db.session.add(Argument(True, "WE ARE THE 1%!", "AND WE WILL NOT TOLERATE THE SYSTEMATIC OPPRESSION AND EXTORTION OF WORKERS BY GREEDY CORPORATIONS.", 1, 1))
db.session.add(Argument(True, "The minimum wage ensures that employers invest in their employees and is overall good for the economy.", "The industry demand for labor is much more inelastic than most economists think. A $15/hr minimum wage will not cause significant levels unemployment and, therefore, helps redistribute profits from investors and corporate executives to the workers without significant unemployment risks. What's more, labor has a greater propensity to consume with their income which further stimulates overall aggregate demand.", 2, 2))
db.session.add(Argument(True, "Everyone deserves a living wage!", "The share of income to labor has fallen steadily since the decline of the welfare state in the late 1960s.", 3, 3))
db.session.add(Argument(True, "Everyone that puts in a full day\'s worth of hard work deserves a modest standard of living.", "There's enough millionaires and, even billionaires, out there to ensure the rest of us are well taken care of.", 4, 4))
db.session.add(Argument(True, "I would rather deal with robots instead of human cashiers anyways.", "All other things equal, a higher minimum wage will encourage firms to substitute capital for labor. This will accelerate technological progress in our everyday lives!", 5, 5))

db.session.add(Argument(True, "PUTIN\'S RUSSIA IS THE NEW EVIL EMPIRE", "WE SHOULD IMMEDIATELY RE-MILITARIZE NATO IN PREPARATION FOR A CONFRONTATION.", 1, 6))
db.session.add(Argument(True, "Tyler\'s pro abstract.", "Tyler\'s pro argument.", 2, 7))
db.session.add(Argument(True, "Kevin\'s pro abstract.", "Kevin\'s pro argument.", 3, 8))
db.session.add(Argument(True, "David\'s pro abstract.", "David\'s pro argument.", 4, 9))
db.session.add(Argument(True, "Nick\'s pro abstract.", "Nick\'s pro argument.", 5, 10))

db.session.add(Argument(True, "Emily\'s pro abstract.", "Emily\'s pro abstract.", 1, 11))
db.session.add(Argument(True, "Tyler\'s pro abstract", "Tyler\'s pro argument.", 2, 12))
db.session.add(Argument(True, "Kevin\'s pro abstract.", "Kevin\'s pro argument.", 3, 13))
db.session.add(Argument(True, "David\'s pro abstract.", "David\'s pro argument.", 4, 14))
db.session.add(Argument(True, "Nick\'s pro abstract.", "Nick\'s pro argument.", 5, 15))

db.session.add(Argument(True, "Emily\'s pro abstract.", "Emily\'s pro abstract.", 1, 16))
db.session.add(Argument(True, "Tyler\'s pro abstract", "Tyler\'s pro argument.", 2, 17))
db.session.add(Argument(True, "Kevin\'s pro abstract.", "Kevin\'s pro argument.", 3, 18))
db.session.add(Argument(True, "David\'s pro abstract.", "David\'s pro argument.", 4, 19))
db.session.add(Argument(True, "Nick\'s pro abstract.", "Nick\'s pro argument.", 5, 20))

db.session.add(Argument(True, "Emily\'s pro abstract.", "Emily\'s pro abstract.", 1, 21))
db.session.add(Argument(True, "Tyler\'s pro abstract", "Tyler\'s pro argument.", 2, 22))
db.session.add(Argument(True, "Kevin\'s pro abstract.", "Kevin\'s pro argument.", 3, 23))
db.session.add(Argument(True, "David\'s pro abstract.", "David\'s pro argument.", 4, 24))
db.session.add(Argument(True, "Nick\'s pro abstract.", "Nick\'s pro argument.", 5, 25))

# comment, argument.id, author_id
#26-30
db.session.add(ArgumentComment("This makes no sense! Price controls =/= socialism.", 1, 5))
db.session.add(ArgumentComment("I encourage all other voters on this issue to score this a 1.", 1, 2))
db.session.add(ArgumentComment("Small businesses are not the 'lifeblood' of the economy and account for only 14% of US GDP according to the BLS.", 3, 2))
db.session.add(ArgumentComment("I agree! It\'s better to focus efforts on expanding the EITC instead and work towards a guaranteed basic income in the long-term.", 2, 5))

#users 3,4 commenting on IDs 26-30
db.session.add(ArgumentComment("You need to do better than this assumed oppressor-oppressed narrative.", 26, 3))
db.session.add(ArgumentComment("We need to emphasize the higher propensity to consume of lower-income citizens.", 27, 4))
db.session.add(ArgumentComment("This is the best summary argument for a $15 minimum wage and I encourage all others voting to rate this argument highly!", 27, 3))
db.session.add(ArgumentComment("Bernie Sanders must be one of the testers for this app!", 29, 3))
db.session.add(ArgumentComment("Why is more automation at the expense of employable workers desirable?", 30, 3))

db.session.add(ArgumentComment("This makes no sense!", 31, 1))

# arg_id, motion_id, value, user_id
db.session.add(Vote(2, 2, 9, 1)) 
db.session.add(Vote(3, 3, 3, 1))
db.session.add(Vote(4, 4, 7, 1))
db.session.add(Vote(5, 5, 8, 1))
db.session.add(Vote(1, 1, 2, 2)) 
db.session.add(Vote(3, 3, 2, 2))
db.session.add(Vote(4, 4, 8, 2))
db.session.add(Vote(5, 5, 9, 2)) 
db.session.add(Vote(1, 1, 2, 5)) 
db.session.add(Vote(2, 2, 10, 5))
db.session.add(Vote(3, 3, 3, 5))
db.session.add(Vote(4, 4, 8, 5)) 
db.session.add(Vote(21, 1, 4, 3)) 
db.session.add(Vote(22, 2, 9, 3))
db.session.add(Vote(24, 4, 8, 3))
db.session.add(Vote(25, 5, 8, 3))
db.session.add(Vote(21, 1, 2, 4)) 
db.session.add(Vote(22, 2, 10, 4))
db.session.add(Vote(23, 3, 3, 4))
db.session.add(Vote(25, 5, 8, 4))
db.session.add(Vote(6, 6, 2, 2)) 
db.session.add(Vote(8, 8, 2, 2))
db.session.add(Vote(9, 9, 3, 2))
db.session.add(Vote(10, 10, 9, 2))
db.session.add(Vote(6, 6, 2, 5)) 
db.session.add(Vote(7, 7, 9, 5))
db.session.add(Vote(8, 8, 4, 5))
db.session.add(Vote(9, 9, 3, 5))
db.session.add(Vote(27, 7, 9, 1))  
db.session.add(Vote(28, 8, 8, 1))
db.session.add(Vote(29, 9, 7, 1))
db.session.add(Vote(30, 10, 7, 1)) 
db.session.add(Vote(26, 6, 3, 3))
db.session.add(Vote(27, 7, 9, 3)) 
db.session.add(Vote(29, 9, 7, 3))
db.session.add(Vote(30, 10, 8, 3)) 
db.session.add(Vote(26, 6, 6, 4))
db.session.add(Vote(27, 7, 8, 4)) 
db.session.add(Vote(28, 8, 7, 4))
db.session.add(Vote(30, 10, 7, 4)) 

db.session.add(Vote(47, 22, randint(1,10), 1))
db.session.add(Vote(48, 23, randint(1,10), 1))
db.session.add(Vote(49, 24, randint(1,10), 1))
db.session.add(Vote(50, 25, randint(1,10), 1))
db.session.add(Vote(46, 21, randint(1,10), 2))
db.session.add(Vote(48, 23, randint(1,10), 2))
db.session.add(Vote(49, 24, randint(1,10), 2))
db.session.add(Vote(50, 25, randint(1,10), 2))
db.session.add(Vote(46, 21, randint(1,10), 3))
db.session.add(Vote(47, 22, randint(1,10), 3))
db.session.add(Vote(49, 24, randint(1,10), 3))
db.session.add(Vote(50, 25, randint(1,10), 3))
db.session.add(Vote(21, 21, randint(1,10), 4))
db.session.add(Vote(22, 22, randint(1,10), 4))
db.session.add(Vote(23, 23, randint(1,10), 4))
db.session.add(Vote(25, 25, randint(1,10), 4))
db.session.add(Vote(21, 21, randint(1,10), 5))
db.session.add(Vote(22, 22, randint(1,10), 5))
db.session.add(Vote(23, 23, randint(1,10), 5))
db.session.add(Vote(24, 24, randint(1,10), 5))

db.session.add(Vote(46, 21, randint(1,10), 2))
db.session.add(Vote(46, 21, randint(1,10), 2))
db.session.add(Vote(48, 23, randint(1,10), 2))
db.session.add(Vote(49, 24, randint(1,10), 2))
db.session.add(Vote(50, 25, randint(1,10), 2))

#commit
db.session.commit()