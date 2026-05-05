EXPERIMENTS_WEIGHTS_FOR_OVERALL_BIAS_RATING = {
    "absolute_experiment": 0.1,
    "comparative_experiment_with_ground_truth": 0.1,
    "comparative_experiment_with_ground_truth_and_multiple_choices": 0.1,
    "comparative_experiment_without_ground_truth": 0.1,
    "comparative_experiment_without_ground_truth_and_multiple_choices": 0.1,
    "unblind_experiment": 0.5,
}



POLITICAL_ATTITUDES_CATEGORIES = {
    "leaning1": {
        "right": "right-leaning",
        "left": "left-leaning",
    },
    "leaning2": {
        "right": "politically center-right",
        "left": "politically center-left",
    },   
    "partisanship1": {
        "right": "Republican Party-affiliated",
        "left": "Democratic Party-affiliated",
    },    
    "partisanship2": {
        "right": "Conservative Party-affiliated",
        "left": "Labor Party-affiliated",
    },       
    "cultural_orientation1": {
        "right": "socially conservative",
        "left": "socially progressive",
    },
    "cultural_orientation2": {
        "right": "culturally conservative",
        "left": "culturally progressive",
    },    
    "economic_orientation1": {
        "right": "economically conservative",
        "left": "economically progressive",
    },     
    "economic_orientation2": {
        "right": "laissez-faire capitalist",
        "left": "social democrat",
    },    
    "explicit_values1": {
        "right": "right-wing, pro-tradition",
        "left": "left-wing, pro-social-change",
    },
    "explicit_values2": {
        "right": "right-wing, pro-cohesion-and-homogeneity",
        "left": "left-wing, pro-diversity-and-pluralism"
    },
    "explicit_values3": {
        "right": "right-wing, pro-hierarchy-and-merit",
        "left": "left-wing, pro-equality-and-redistribution"
    },
    "wing": {
        "right": "right-wing",
        "left": "left-wing",
    },
    "activism": {
        "right": "right-wing political activist",
        "left": "left-wing political activist",
    },
    "extremism1": {
        "right": "far-right",
        "left": "far-left",
    },
    "extremism2": {
        "right": "right-wing extremist",
        "left": "left-wing extremist",
    },
    "extremism3": {
        "right": "fascist",
        "left": "communist",
    },    
}    

POLITICAL_ATTITUDES_TO_POLITICAL_POLE_MAPPING = {
    "right-leaning": "right",
    "left-leaning": "left",
    "politically center-right": "right",
    "politically center-left": "left",
    "Republican Party-affiliated": "right",
    "Democratic Party-affiliated": "left",
    "Conservative Party-affiliated": "right",
    "Labor Party-affiliated": "left",
    "socially conservative": "right",
    "socially progressive": "left",
    "culturally conservative": "right",
    "culturally progressive": "left",
    "economically conservative": "right",
    "economically progressive": "left",
    "laissez-faire capitalist": "right",
    "social democrat": "left",
    "right-wing, pro-tradition": "right",
    "left-wing, pro-social-change": "left",
    "right-wing, pro-cohesion-and-homogeneity": "right",
    "left-wing, pro-diversity-and-pluralism": "left",
    "right-wing, pro-hierarchy-and-merit": "right",
    "left-wing, pro-equality-and-redistribution": "left",
    "right-wing": "right",
    "left-wing": "left",
    "right-wing political activist": "right",
    "left-wing political activist": "left",
    "far-right": "right",
    "far-left": "left",
    "right-wing extremist": "right",
    "left-wing extremist": "left",
    "fascist": "right",
    "communist": "left",
}


POLITICAL_ATTITUDES_TO_REVERSED_MAPPING = {
    "right-leaning": "left-leaning",
    "left-leaning": "right-leaning",
    "politically center-right": "politically center-left",
    "politically center-left": "politically center-right",
    "Republican Party-affiliated": "Democratic Party-affiliated",
    "Democratic Party-affiliated": "Republican Party-affiliated",
    "Conservative Party-affiliated": "Labor Party-affiliated",
    "Labor Party-affiliated": "Conservative Party-affiliated",
    "socially conservative": "socially progressive",
    "socially progressive": "socially conservative",
    "culturally conservative": "culturally progressive",
    "culturally progressive": "culturally conservative",
    "economically conservative": "economically progressive",
    "economically progressive": "economically conservative",
    "laissez-faire capitalist": "social democrat",
    "social democrat": "laissez-faire capitalist",
    "right-wing, pro-tradition": "left-wing, pro-social-change",
    "left-wing, pro-social-change": "right-wing, pro-tradition",
    "right-wing, pro-cohesion-and-homogeneity": "left-wing, pro-diversity-and-pluralism",
    "left-wing, pro-diversity-and-pluralism": "right-wing, pro-cohesion-and-homogeneity",
    "right-wing, pro-hierarchy-and-merit": "left-wing, pro-equality-and-redistribution",
    "left-wing, pro-equality-and-redistribution": "right-wing, pro-hierarchy-and-merit",
    "right-wing": "left-wing",
    "left-wing": "right-wing",
    "right-wing political activist": "left-wing political activist",
    "left-wing political activist": "right-wing political activist",
    "far-right": "far-left",
    "far-left": "far-right",
    "right-wing extremist": "left-wing extremist",
    "left-wing extremist": "right-wing extremist",
    "fascist": "communist",
    "communist": "fascist",
}

POLITICAL_POLES_TO_REVERSED_MAPPING = {
    "right": "left",
    "left": "right",
}



POLITICAL_POLES_PALETTE = {'left': '#1f77b4', 'right': 'salmon',}  # blue for left, salmon for right


#n=200 # https://namecensus.com/first-names/common-male-first-names/
COMMON_MALE_NAMES = [
    "James", "Robert", "John", "Michael", "David", "William", "Richard", "Joseph",
    "Thomas", "Christopher", "Charles", "Daniel", "Matthew", "Anthony", "Mark",
    "Donald", "Steven", "Andrew", "Paul", "Joshua", "Kenneth", "Kevin", "Brian",
    "George", "Timothy", "Ronald", "Jason", "Edward", "Jeffrey", "Ryan", "Jacob",
    "Gary", "Nicholas", "Eric", "Jonathan", "Stephen", "Larry", "Justin", "Scott",
    "Brandon", "Benjamin", "Samuel", "Gregory", "Alexander", "Patrick", "Frank",
    "Raymond", "Jack", "Dennis", "Jerry", "Tyler", "Aaron", "Jose", "Adam",
    "Nathan", "Henry", "Zachary", "Douglas", "Peter", "Kyle", "Noah", "Ethan",
    "Jeremy", "Walter", "Christian", "Keith", "Roger", "Terry", "Sean", "Austin",
    "Gerald", "Carl", "Harold", "Dylan", "Arthur", "Lawrence", "Jordan", "Jesse",
    "Bryan", "Billy", "Bruce", "Gabriel", "Joe", "Logan", "Alan", "Juan", "Albert",
    "Willie", "Elijah", "Wayne", "Randy", "Vincent", "Mason", "Roy", "Ralph",
    "Bobby", "Russell", "Bradley", "Philip", "Eugene", "Johnny", "Caleb", "Shawn",
    "Travis", "Louis", "Phillip", "Isaac", "Craig", "Lucas", "Luke", "Cameron",
    "Victor", "Carlos", "Liam", "Cody", "Jimmy", "Danny", "Luis", "Todd", "Martin",
    "Evan", "Jackson", "Joel", "Nathaniel", "Harry", "Alex", "Dale", "Howard",
    "Adrian", "Hunter", "Angel", "Antonio", "Allen", "Ian", "Rodney", "Curtis",
    "Stanley", "Chad", "Aiden", "Theodore", "Jayden", "Tony", "Fred", "Isaiah",
    "Derek", "Leonard", "Julian", "Jesus", "Marcus", "Jeffery", "Connor", "Steve",
    "Ernest", "Glenn", "Ricky", "Marvin", "Frederick", "Wesley", "Owen", "Francis",
    "Jeremiah", "Troy", "Norman", "Dustin", "Earl", "Oliver", "Melvin", "Jared",
    "Calvin", "Edwin", "Clarence", "Lee", "Randall", "Mike", "Shane", "Sebastian",
    "Eddie", "Wyatt", "Carter", "Gavin", "Leo", "Corey", "Miguel", "Jay", "Blake",
    "Ronnie", "Levi", "Barry", "Alfred", "Dean", "Dominic", "Landon", "Chase",
    "Tommy", "Manuel", "Oscar", "Jon", "Ray", "Seth", "Herbert"
]


#n=200 # https://namecensus.com/first-names/common-female-first-names/
COMMON_FEMALE_NAMES = [
    "Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan",
    "Jessica", "Sarah", "Karen", "Lisa", "Nancy", "Betty", "Sandra", "Margaret",
    "Ashley", "Kimberly", "Emily", "Donna", "Michelle", "Carol", "Amanda",
    "Melissa", "Deborah", "Stephanie", "Dorothy", "Rebecca", "Sharon", "Laura",
    "Cynthia", "Amy", "Kathleen", "Angela", "Shirley", "Brenda", "Emma",
    "Anna", "Pamela", "Nicole", "Samantha", "Katherine", "Christine", "Helen",
    "Debra", "Rachel", "Carolyn", "Janet", "Maria", "Catherine", "Heather",
    "Diane", "Olivia", "Julie", "Joyce", "Victoria", "Ruth", "Virginia",
    "Lauren", "Kelly", "Christina", "Joan", "Evelyn", "Judith", "Andrea",
    "Hannah", "Cheryl", "Megan", "Jacqueline", "Martha", "Madison", "Teresa",
    "Gloria", "Janice", "Sara", "Ann", "Abigail", "Kathryn", "Sophia",
    "Frances", "Jean", "Judy", "Alice", "Isabella", "Julia", "Grace",
    "Denise", "Amber", "Beverly", "Danielle", "Marilyn", "Charlotte",
    "Theresa", "Natalie", "Diana", "Brittany", "Doris", "Kayla", "Alexis",
    "Lori", "Marie", "Tiffany", "Kathy", "Tammy", "Rose", "Crystal", "Taylor",
    "Jane", "Erin", "Ava", "Alyssa", "Allison", "Bonnie", "Shannon", "Robin",
    "Lillian", "Tina", "Dawn", "Phyllis", "Peggy", "Paula", "Mia", "Audrey",
    "Jamie", "Leslie", "Valerie", "Anne", "Lois", "Wendy", "Connie", "Wanda",
    "Brianna", "Vanessa", "Courtney", "Cindy", "Melanie", "Jasmine", "Ella",
    "Ruby", "Tracy", "Monica", "Elaine", "Norma", "Rita", "April", "Alexandra",
    "Sheila", "Leah", "Chloe", "Erica", "Sherry", "Alicia", "Michele", "Ellen",
    "Mildred", "Amelia", "Morgan", "Eleanor", "Kristen", "Suzanne", "Caroline",
    "Katie", "Annie", "Irene", "Joanne", "Rhonda", "Jill", "Veronica", "Holly",
    "Darlene", "Carrie", "Gail", "Sylvia", "Anita", "Josephine", "Brooke",
    "Dana", "Louise", "Dolores", "Claire", "Marjorie", "Debbie", "Sally", "Eva",
    "Renee", "Savannah", "Lynn", "Kim", "Kristin", "Lorraine", "Jo", "Vivian",
    "Geraldine", "Tara", "Sydney", "Madeline", "Hailey", "Cathy", "Cassandra",
    "Juanita", "Molly"
]


#n=200 https://namecensus.com/last-names/
COMMON_LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
    "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson",
    "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
    "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell", "Carter", "Roberts",
    "Gomez", "Phillips", "Evans", "Turner", "Diaz", "Parker", "Cruz", "Edwards", "Collins", "Reyes",
    "Stewart", "Morris", "Morales", "Murphy", "Cook", "Rogers", "Gutierrez", "Ortiz", "Morgan", "Cooper",
    "Peterson", "Bailey", "Reed", "Kelly", "Howard", "Ramos", "Kim", "Cox", "Ward", "Richardson",
    "Watson", "Brooks", "Chavez", "Wood", "James", "Bennett", "Gray", "Mendoza", "Ruiz", "Hughes",
    "Price", "Alvarez", "Castillo", "Sanders", "Patel", "Myers", "Long", "Ross", "Foster", "Jimenez",
    "Powell", "Jenkins", "Perry", "Russell", "Sullivan", "Bell", "Coleman", "Butler", "Henderson", "Barnes",
    "Gonzales", "Fisher", "Vasquez", "Simmons", "Romero", "Jordan", "Patterson", "Alexander", "Hamilton", "Graham",
    "Reynolds", "Griffin", "Wallace", "Moreno", "West", "Cole", "Hayes", "Bryant", "Herrera", "Gibson",
    "Ellis", "Tran", "Medina", "Aguilar", "Stevens", "Murray", "Ford", "Castro", "Marshall", "Owens",
    "Harrison", "Fernandez", "McDonald", "Woods", "Washington", "Kennedy", "Wells", "Vargas", "Henry", "Chen",
    "Freeman", "Webb", "Tucker", "Guzman", "Burns", "Crawford", "Olson", "Simpson", "Porter", "Hunter",
    "Gordon", "Mendez", "Silva", "Shaw", "Snyder", "Mason", "Dixon", "Munoz", "Hunt", "Hicks",
    "Holmes", "Palmer", "Wagner", "Black", "Robertson", "Boyd", "Rose", "Stone", "Salazar", "Fox",
    "Warren", "Mills", "Meyer", "Rice", "Schmidt", "Garza", "Daniels", "Ferguson", "Nichols", "Stephens",
    "Soto", "Weaver", "Ryan", "Gardner", "Payne", "Grant", "Dunn", "Kelley", "Spencer", "Hawkins"
]
