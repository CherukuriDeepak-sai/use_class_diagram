"""
Recipe Genie - class model.

Matches the Recipe Genie UML class diagram: the same 20 classes, attributes and methods.
Attributes that hold other objects (dietProfile, steps, ingredients, ...) are the
associations from the diagram.
"""

import uuid
from datetime import datetime


class InputMode:
    """Enumeration."""
    CHAT = "CHAT"
    VOICE = "VOICE"


class User:
    def __init__(self, name, email, password):
        self.userId = uuid.uuid4()
        self.name = name
        self.email = email
        self.passwordHash = str(hash(password))
        self.dietProfile = DietProfile()        # has 1 DietProfile (composition)
        self.sources = []                       # submits 0..* RecipeSource
        self.savedRecipes = []                  # saves 0..* Recipe
        self.sessions = []                      # starts 0..* CookingSession

    def register(self):
        print("Registered", self.email)

    def login(self):
        return "token-" + str(self.userId)

    def updateProfile(self):
        print("Profile updated for", self.name)

    def saveRecipe(self, r, rating):
        self.savedRecipes.append(r)
        print("Saved", r.title, "with rating", rating)


class DietProfile:
    def __init__(self):
        self.dietType = "none"
        self.dailyCalorieGoal = 2000
        self.mealRoutine = ""
        self.allergies = []                     # lists 0..* Allergy (aggregation)

    def buildRoutine(self):
        self.mealRoutine = "3 meals a day"

    def logMeal(self, r):
        print("Logged", r.title)


class Allergy:
    def __init__(self, name, severity):
        self.name = name
        self.severity = severity


class RecipeSource:
    """Abstract class."""

    def __init__(self, inputMode):
        self.sourceId = uuid.uuid4()
        self.inputMode = inputMode
        self.createdAt = datetime.now()


class VideoLink(RecipeSource):
    def __init__(self, url, platform):
        RecipeSource.__init__(self, InputMode.CHAT)
        self.url = url
        self.platform = platform


class Photo(RecipeSource):
    def __init__(self, imageUrl):
        RecipeSource.__init__(self, InputMode.CHAT)
        self.imageUrl = imageUrl


class MoodPrompt(RecipeSource):
    def __init__(self, text, maxMinutes, inputMode):
        RecipeSource.__init__(self, inputMode)
        self.text = text
        self.maxMinutes = maxMinutes


class RecipeGenerator:
    """<<service>>"""

    def fromVideo(self, v):
        return Recipe("Recipe from " + v.platform + " video")

    def fromPhoto(self, p):
        return Recipe("Recipe from photo")

    def suggestByMood(self, m):
        return [Recipe("Idea 1"), Recipe("Idea 2"), Recipe("Idea 3")]


class AllergyChecker:
    """<<service>>"""

    def check(self, r, d):
        names = [a.name for a in d.allergies]
        warnings = []
        for ri in r.ingredients:
            for allergen in ri.ingredient.allergens:
                if allergen in names:
                    warnings.append(ri.ingredient.name + " contains " + allergen)
        return warnings

    def suggestSwap(self, i):
        return Ingredient("Safe alternative to " + i.name, [])


class Recipe:
    def __init__(self, title):
        self.recipeId = uuid.uuid4()
        self.title = title
        self.servings = 2
        self.totalMinutes = 0
        self.calories = 0
        self.difficulty = "Easy"
        self.ingredients = []                   # uses 1..* Ingredient, via RecipeIngredient
        self.steps = []                         # contains 1..* Step (composition)

    def scale(self, servings):
        factor = servings / self.servings
        for ri in self.ingredients:
            ri.quantity = ri.quantity * factor
        self.servings = servings

    def getMissingIngredients(self, pantry):
        have = [p.name for p in pantry]
        return [ri.ingredient for ri in self.ingredients if ri.ingredient.name not in have]


class RecipeIngredient:
    """Association class between Recipe and Ingredient."""

    def __init__(self, ingredient, quantity, unit):
        self.ingredient = ingredient
        self.quantity = quantity
        self.unit = unit


class Ingredient:
    def __init__(self, name, allergens):
        self.ingredientId = uuid.uuid4()
        self.name = name
        self.allergens = allergens


class Step:
    def __init__(self, stepNo, instruction, durationSec):
        self.stepNo = stepNo
        self.instruction = instruction
        self.durationSec = durationSec
        self.imageUrl = ""
        self.clipUrl = ""


class CookingSession:
    def __init__(self, recipe):
        self.sessionId = uuid.uuid4()
        self.startedAt = None
        self.currentStep = 0
        self.recipe = recipe                    # follows 1 Recipe
        self.timers = []                        # times 1..* StepTimer (composition)

    def start(self):
        self.startedAt = datetime.now()

    def nextStep(self):
        self.currentStep = self.currentStep + 1
        return self.recipe.steps[self.currentStep - 1]

    def askForHelp(self, question):
        return "Tip for step " + str(self.currentStep) + ": " + question

    def finish(self):
        print("Finished", self.recipe.title)


class StepTimer:
    def __init__(self, stepNo):
        self.stepNo = stepNo
        self.startTime = None
        self.elapsedSec = 0

    def start(self):
        self.startTime = datetime.now()

    def stop(self):
        self.elapsedSec = int((datetime.now() - self.startTime).total_seconds())
        return self.elapsedSec


class PlaceFinder:
    """<<service>>"""

    def findShops(self, items):
        return [Shop("FreshMart", "12 High Street", 0.4, "8am-10pm")]

    def findRestaurants(self, dish):
        return [Restaurant("Trattoria Bella", "5 Market Road", 0.8, "Italian", 4.5)]


class Place:
    """Abstract class."""

    def __init__(self, name, address, distanceKm):
        self.name = name
        self.address = address
        self.distanceKm = distanceKm

    def getDirections(self):
        return "Directions to " + self.name


class Shop(Place):
    def __init__(self, name, address, distanceKm, openingHours):
        Place.__init__(self, name, address, distanceKm)
        self.openingHours = openingHours


class Restaurant(Place):
    def __init__(self, name, address, distanceKm, cuisine, rating):
        Place.__init__(self, name, address, distanceKm)
        self.cuisine = cuisine
        self.rating = rating
