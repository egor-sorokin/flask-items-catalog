from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Category, Base, CategoryItem

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

categories = ["Soccer", "Basketball", "Frisbee", "Hockey"]


category = Category(name=categories[0])
item = CategoryItem(name="Shorts",
                    description="Lorem ipsum dolor sit amet",
                    category=category)
session.add(item)
session.commit()

item = CategoryItem(name="Ball",
                    description="Lorem ipsum dolor sit amet",
                    category=category)
session.add(item)
session.commit()

item = CategoryItem(name="T-Shirt",
                    description="Lorem ipsum dolor sit amet",
                    category=category)
session.add(item)
session.commit()
item = CategoryItem(name="Shoes",
                    description="Lorem ipsum dolor sit amet",
                    category=category)
session.add(item)
session.commit()



category = Category(name=categories[1])
item = CategoryItem(name="Hat",
                    description="Lorem ipsum dolor sit amet",
                    category=category)
session.add(item)
session.commit()

item = CategoryItem(name="T-Shirt",
                    description="Lorem ipsum dolor sit amet",
                    category=category)
session.add(item)
session.commit()

item = CategoryItem(name="Snickers",
                    description="Lorem ipsum dolor sit amet",
                    category=category)
session.add(item)
session.commit()



category = Category(name=categories[2])
item = CategoryItem(name="T-Shirt",
                    description="Lorem ipsum dolor sit amet",
                    category=category)
session.add(item)
session.commit()
item = CategoryItem(name="Snickers",
                    description="Lorem ipsum dolor sit amet",
                    category=category)
session.add(item)
session.commit()




category = Category(name=categories[3])
item = CategoryItem(name="Helmet",
                    description="Lorem ipsum dolor sit amet",
                    category=category)
session.add(item)
session.commit()

item = CategoryItem(name="T-Shirt",
                    description="Lorem ipsum dolor sit amet",
                    category=category)
session.add(item)
session.commit()

item = CategoryItem(name="Hockey-stick",
                    description="Lorem ipsum dolor sit amet",
                    category=category)
session.add(item)
session.commit()

print "added catalog items!"
