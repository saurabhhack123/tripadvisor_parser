# tripadvisor_parser

# Help a mentee @ Codementor to build this project 

Requirements for this phase of the project

* Choose a Deep Web source of your choice from one of the domains: Hotels (e.g., Booking, Hotels), Restaurants (e.g., Tripadvisor, OpenTable, and Yelp), Movies (e.g., Redbox, rotedtomato) Books (Barnesandnoble), or Electronics (Amazon, Newegg). Let's call L the website of your choice.
* Automatically issue queries to L.
* Determine whether L returns any result to your query.
* L usually returns hundreds of records to a user query. The results are organized in pages, usually a page contains 10 or 20 records per page. Hence, in order to gather the records returned to a user query you need to traverse all those pages.
* Each record has its own page that contain detailed information about an entity. For example, if the web site is from the Restaurant domain, for each restaurant the web site will provide pieces of data such as Address, Phone, Name, and Cuisine. Some web sites may even provide user reviews. Your crawler will need to collect all such data about a restaurant.
* If the web site has user reviews, the reviews may also span multiple pages. Again, you will need to traverse all those pages and collect the data.

