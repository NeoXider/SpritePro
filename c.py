class Cat:
    def __init__(self, name, age, text_may):
        self.name = name
        self.age = age
        self.may = text_may

    def info(self):
        print(f"I am a cat. My name is {self.name}. I am {self.age} years old.")

    def make_sound(self):
        print(self.may)

    def jump(self, jump):
        print(f"i m jump: {jump}")


class Dog:
    def info(self):
        print(f"I am a dog. My name is {self.name}. I am {self.age} years old.")

    def make_sound(self):
        print(self.may)


barsic = Cat("barsic", 2, "mrr")
barsic.info()
barsic.make_sound()
barsic.jump(5)
Cat.jump(barsic, 5)

cat2 = Cat(1, 1, 1)
cat2.jump(2)

print("=========\n")
