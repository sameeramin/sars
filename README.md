# Scientific Artilcles Recommendation System (SARS)
A web-based scientific articles recommendations system that recommends scientific articles of user interest based on text classification Doc2Vec modeling scheme and cosine similarity measure.

## Functionalites
### Sign Up
A Signup module from which users will be required to register themself in the application. The
user will get registered once the admin will approve it.

### Sign In
Only registered users can log into the application.

### Manage Users
Admin can manage users means it can approve user, remove users and view user data through admin dashboard.

### Add Scientific Articles
Admin can add scientific articles data to the database having abstract and area
through admin dashboard. Once a new article is added the model training will be triggered autmatically.

### Recommend Scientific Articles Using Cosine Similarity Measure
A webpage which takes article abstract which is not added yet in the system as
input by the user and on clicking generate recommendations the application infers user article vector. Then it shows articles recommendations by computing cosine similarity
between user vector and already added article vectors in descending order.

## Tools
- Django
- SQLite3
- Bootstrap
- Gensim
- NLTK
- Numpy & SciPy
- Pandas
