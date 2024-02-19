In this project, I set up some code for web scraping sports odds data from some German bookmakers. 

My goal was to analyze if there are arbitrage opportunities, i.e. combinations of odds for a given match across multiple bookmakers such that one can place bets with a riskfree profit (sure bets). Example:
- Odds team A by bookmaker B1: 1.8 
- Odds team B by bookmaker B2: 2.4
One can place 1/1.8 of available credits on team A at bookmaker B1 and 1/2.4 on team B at bookmaker B2, which results in a riskfree profit of 1 - 1/1.8 - 1/2.4 = 2.8%

The main work that had to be done was:
- Create an abstract parser class with shared tools
- Implement specific parsers based on abstract parent class for each of the four bookmakers
- Collect and unify data
- Store data in some database (I used Mongodb Atlas)
- Implement a function that computes those arbitrage opportunities (by comparing all combination across all bookmakers)

I used:
- Selenium for the webscraping part
- Pandas for data analysis

