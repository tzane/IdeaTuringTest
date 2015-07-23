import sqlite3

with sqlite3.connect("sample.db") as connection:
    c = connection.cursor()
    c.execute("CREATE TABLE arguments(user INTEGER, topic TEXT, procon_topic INTEGER, user_procon INTEGER, argument_abstract TEXT, argument TEXT)")
    c.execute('INSERT INTO arguments VALUES(1, "Minimum wage", 0, 0, "DON\'T TREAD ON ME!", "OBAMA\'S NEW SOCIALISM IS ALL ABOUT GOVERNMENT HANDOUTS TO THE POOR AND LAZY")')
    c.execute('INSERT INTO arguments VALUES(2, "Minimum wage", 0, 0, "The minimum wage is relatively high-risk to vulnerable workers and is poor a policy choice relative to other politically feasible options.", "Although the employment effects are empirically mixed, we should not risk pricing vulnerable low-skilled workers out of the labor market and passing on higher costs to consumers in these industries (most of whom are themselves low-income consumers). There are other politically feasible policy options which are low-risk to workers and directly target poverty. These policy options include direct cash subsidies (e.g. basic income or negative income tax) and refundable tax credits (e.g. earned income tax credits).")')
    c.execute('INSERT INTO arguments VALUES(3, "Minimum wage", 0, 1, "The minimum wage hurts small businesses more than large corporations.", "Small businesses are the lifeblood of the American economy and increases in the minimum wage will destroy these jobs. Why stop at $15 an hour? Why not $100 an hour?! Why not just pay everyone in cocaine and unicorns?")')
