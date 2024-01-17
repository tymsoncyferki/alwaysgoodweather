## alwaysgoodweather

You better check on [alwaysgoodweather.com](https://alwaysgoodweather.shinyapps.io/forecast/)!

### Motivation

This app (and amount of work put into it) may not make much sense to you, but it's just my dad's rolling joke
and I always wanted to bring it to life. Apart from that I wanted to learn Shiny for Python and plotnine - 
equivalents of R Shiny and ggplot. 

Check out what it looks like:

![World Map](https://github.com/tymsoncyferki/alwaysgoodweather/blob/main/readme_files/app.png)

### About the app

The aim of this web app, however it sounds, is to always show good weather. The only problem is how to make displayed
temperature possible in given location. I can't just set it between 20 and 30 Celsius degrees, because it is impossible 
in Fairbanks during the winter. My approach was to create a dozen of points around the world, appoint desired
(and possible) temperature intervals and create a model (yes, I really wanted to include some machine learning), 
which calculates desired temperature interval for given location. Then the real current temperature is scaled to this
interval.

With my model I can generate average temperatures for the whole world based on just a couple of points:

![World Map](https://github.com/tymsoncyferki/alwaysgoodweather/blob/main/readme_files/world.png)




