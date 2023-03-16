# CarCost
tldr: Quick guide is present in application.

## About
As written in the repository's description this is an application with GUI which is designed to give you an idea of what is your car's value. In order to answer that question it will need data which it gets by on demand scraping the used cars market called www.autobazar.eu. Following it in order to predict your's car value this application offers 2 prediction methods. Those being k-nearest neighbours and neural network based predictor. It is recommended to use k-nearest neighbours if scraped amount of cars from car market is low. Otherwise those 2 methods can produce quite similiar results although the neural network predictor tends to be more sensitive towards it's settings.  

## Requirements to run
As this application is written in Python you will need that installed on your system. GUI is written using Tkinter which should come with Python. The application also uses following libraries which you will need to have installed:
- TensorFlow
- NumPy
- Pandas
- Selenium
## Guide 
1. When you start the application it will also open it's Chrome tab in which the scraper will work. Do not close it. Initial frame of the application also contains quick guide as a faster although less detailed alternative to this guide.

| ![Application turned on](./readme_images/initial.png) | 
|:--:| 
| What you see when you start the application |



By Samuel Mintál