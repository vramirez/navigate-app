help me create a mobile/web app with javascript as frontend (react) and backend with python (django), please analyze which frameworks are best suited for me as I'm mostly a python/Java debveloper. Keep in mind that this application will use machine learning and advancced AI. The idea of this app is to throw recommendations for busines owners and managers based on local news, news papers, social media posts, to take some action. For example, if you're a pub/bar owner and there's a football (soccer) match in your town, then you could create some campaign attractig fans and/or increase beverage inventory.
the idea is that this app will serve initially coffee shops, restaurants, pubs and bookstores. This will be initially launched in Colombia, so primary language for the frontend should be spanish with option to switch to english. Once you set up business profile, , the app will read and fetch local and national newspapers, and also social media, to get you news related to your business based on analyzing keywords like date, type of business, type of event, etc.

## Data Sources Strategy
- **News Media** - Local newspapers, online news sites
- **Social Media** - Facebook Events, Instagram local posts, Twitter updates  
- **Online Communities** - Local Facebook groups, Reddit communities, WhatsApp neighborhood groups
- **Manual Input** - Business owner observations, customer feedback, local insights
- **Event Platforms** - Eventbrite, Facebook Events, Meetup
- **Government Sources** - Municipal announcements, construction permits, tourism board
- **Academic Calendars** - University schedules, graduation dates, student events
- **Weather & Seasonal** - Climate impacts on outdoor dining, festival cancellations
- **Sports & Culture** - Local team games, cultural festivals, religious holidays
- **Real Estate** - New developments, commercial openings, demographic shifts
You should initially fill a list, but admin should be able to manage this list (CRUD)

## make initial a mock
create a branch called mock where should be all main functionality (recommendation engine) working but the news/social media fetcher. This is for demo purposes only and should allow to show recommendations for a fixed 6 different news of events (mocks too): like a marathon or a gastronomy festival taking place in the corresponding city. It should allow you to change all your profile info and based on that update your recomendations.

## Database
Let's build this initially on sqlite, unless there's something on the requirements that makes you think of another db engine. Engine should store the articles metadata: source, date, section, header, etc, and for social media post: social media link, account, text description and image description (if post has image). Also list of news media sites. Initially build a list of top newspapers in Colombia, classify them by city

## Development best practices
You are an experienced full-stack developer with deep knowledge not only in front and back end but on development best practices, you write well documented software, where not necesarily document each line but important stuff that may not be clear, and also use clear and almost self explanatory variables, methods, functions, class names, etc. You are eager to take advantage of each programming language constructs that help you write cleaner code. Also you know how to build and deploy ml engines using proven stoa techniques. You apply constantly lessons 


## Profile
Every business should be able to store their profile: name, type of business, city (which for now should be (Medellin, Bogota, cartagena and Barranquilla)and a short description about the business, and we will also have an admin profile which should be able to manage a list of newspapers and social media accounts based on cities. Admin should also be able to create customers account initially. 

## Recommendations engine
The recomendation engine is the heart and secret sauce of this product. As it takes all the profile information and per every news/social media post it should extract significant information such as type of event (for example a marathon, a concert, a protest, etc), event date, duration, and any oher feature that will help to make a solid business recommendation. Dive on feature engineering to help select the best features that could be extracted from a news or social media post

## Key Use Case Demonstrated
**Cafetería + Maratón**: When a marathon is announced for 2 weeks away, the system generates fully localized Spanish recommendations:
- **Estrategia de Personal para Evento (ALTO)**: "Contratar 2 baristas adicionales para el período del evento"
- **Preparación Estratégica de Inventario (ALTO)**: "Aumentar inventario 150-200% para bebidas, bebidas energéticas, snacks rápidos"

## I18n
Language switching instantly converts to English equivalents while preserving all user progress and form state.

## Documentation
Claude and readme mds should be updated after every iteration to reflect the latest state of the repository

## Scalability
Keep in mind all "initially" as they mean, based on success those will need to be scaled up


## Git
Please make this a git repository called navitest-app, should have an staging branch called develop and gitshould ignore the claude md file

## Testing
Create a folder called test for internal and temporary creating files for testing and/or debugging. After finishing with them, clean the content of test. This test folder should be excluded from git

## Backlog
For managing backlog tasks, add, remove and manage task in the backlog.md file

## Business Impact Potential
- **Target Market**: Local businesses starting with hospitality sector in Colombian cities, expanding to universal business application
- **Value Proposition**: Smart business assistant providing comprehensive intelligence from multiple data sources including news, social media, communities, and manual input
- **Revenue Model**: SaaS subscription, per-business pricing with tiered data source access and business type expansion
- **Competitive Advantage**: Multi-source intelligence platform with business-specific optimization and local market expertise

Please ask anything you have doubts in proceeding