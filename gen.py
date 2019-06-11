import itertools
import random
import argparse

#декоратор, преобразующий число в многочлен нулевой степени
def int2Polynomial(func):
    def wrapper(self, p):
        if type(p) == int:
            p = Polynomial([p])
        return func(self, p)
    return wrapper

#класс, описывающий многочлен. factors - коэффициенты в порядке убывания степени
class Polynomial:

    def __init__(self, factors = []):
        self.factors = factors

    def degree(self):
        return len(self.factors)

#арифметика при помощи python magic methods
    @int2Polynomial
    def __add__(self, p):
        longer = self 
        shorter = p
        if self.degree() < p.degree():
            longer = p
            shorter = self
        factors = [factor for factor in longer.factors]
        for i in range(longer.degree() - shorter.degree(), longer.degree()):
            factors[i] = factors[i] + shorter.factors[i - longer.degree()]
        return Polynomial(factors)

    def __iadd__(self, p):
        self = self + p
        return self

    def __neg__(self):
        factors = []
        for factor in self.factors:
            factors.append(-factor)
        return Polynomial(factors)

    def __sub__(self, p):
        return self + -p

    @int2Polynomial
    def __mul__(self, p):
        res = Polynomial()
        for degree, factor in enumerate(self.factors[::-1]):
            maxdegree = degree + p.degree()
            factors = [0 for i in range(maxdegree)]
            for pdegree, pfactor in enumerate(p.factors[::-1]):
                factors[maxdegree - (degree + pdegree) - 1] = factor * pfactor
            res +=  Polynomial(factors)
        return res

    @int2Polynomial
    def __divmod__(self, p):
        res = Polynomial()
        temp = Polynomial([fact for fact in self.factors])
        for num in range(len(temp.factors)):
            factor = temp.factors[num]
            degree = self.degree() - num 
            if degree < p.degree():
                break
            #создание многочлена - множителя
            quotient = Polynomial([factor / p.factors[0]] + [0] * (degree -
            p.degree()))
            print(temp, p*quotient)
            temp -= (p * quotient)
            res += quotient
        return res, temp

    def __truediv__(self, other):
        return divmod(self, other)[0]

    def __mod__(self, other):
        return divmod(self, other)[1]

    def __bool__(self):
        for factor in self.factors:
            if factor != 0:
                return True
        return False

    def __str__(self):
        res = ''
        for degree, factor in enumerate(self.factors[::-1]):
            if factor != 0:
                signed = ""
                if factor != 1:
                    signed = "%+d" % int(factor) if degree != self.degree() - 1 else "%d" % int(factor) 
                else:
                    signed = ["+1","-1"][factor < 0]
                xdegree = ""
                if degree == 1:
                    xdegree = "x"
                elif degree > 1:
                    xdegree = "x^%s" % (degree)
                res = "%s%s" % (signed, xdegree) + res
        return res

    def __repr__(self):
        return str(self)

def EvcAlg(a, b):
    multipliers = [Polynomial([1,0]), Polynomial([0,1])]
    while a and b:
        if a > b:
            quot, a = divmod(a,b)
            multipliers[0] -= multipliers[1] * quot
        else:
            quot, b = divmod(b,a)
            multipliers[1] -= multipliers[0] * quot
    if not a:
        return b, multipliers[1].factors
    return a, multipliers[0].factors

#декоратор, преобразующий число в вычет
def int2ModInt(func):
    def wrapper(self, m):
        if type(m) == int:
           m = ModInt(m, self.base) 
        return func(self, m)
    return wrapper

#класс вычета, base - основание, value - значение
class ModInt():

    def __init__(self, value, base):
        self.base = base
        self.value = value % self.base

#арифметика при помощи python magic methods
    @int2ModInt
    def __add__(self, other):
        return ModInt(self.value + other.value, self.base)

    @int2ModInt
    def __iadd__(self, other):
        self.__init__(self.value + other.value, self.base)
        return self

    def __radd__(self, other):
        return self + other

    def __neg__(self):
        return ModInt(self.base - self.value, self.base)


    @int2ModInt
    def __mul__(self, other):
        return ModInt(self.value * other.value, self.base)

    @int2ModInt
    def __truediv__(self, other):
        if not self.value:
            return ModInt(0, self.base)
        gcd, mul = EvcAlg(other.value, self.base)
        if gcd != 1:
            raise ValueError
        #mul[0] - обратный элемент в кольце по модулю base
        return ModInt(self.value * mul[0], self.base)

    @int2ModInt
    def __eq__(self,other):
        return self.value == other.value

    @int2ModInt
    def __lt__(self, other):
        return self.value < other.value
    @int2ModInt
    def __gt__(self, other):
        return self.value > other.value

    def __repr__(self):
        return "value:%s base:%s" % (self.value, self.base)

    def __int__(self):
        return self.value

    def __str__(self):
        return str(self.value)

#метод для конвертации массива чисел в массив вычетов с заданным основанием
def ModIntList(intlist, base):
    return list(map(lambda i: ModInt(i, base), intlist))

#функция-генератор многочленов заданной степени над заданным полем вычетов
def gen_all_polynomials(degree, base):
    for pol in itertools.product(range(1,base), *[range(0,base) for i in range(degree)]):
       yield Polynomial(ModIntList(pol, base)) 

#создание случайного многочлена над полем с заданным основанием
def generate_random_polynomial(degree, base):
    pol = [random.randrange(1,base)]
    pol += [random.randrange(0, base - 1) for i in range(degree)]
    return Polynomial(ModIntList(pol, base))

#проверка многочлена на неприводимость путём деления его на все многочлены 1 и 2 степеней в заданном поле
def is_irreducible(p, base):
    for test in itertools.chain(gen_all_polynomials(1,3),gen_all_polynomials(2,3)):
        if not p % test:
            return False
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    #при вызове программы возможно указать 3 аргумента:
    #randseed - сид для генерации многочленов;
    #taskfile - файл для вывода задания;
    #answerfile - файл для вывода ответа
    parser.add_argument("-randseed", type = str, default = "1")
    parser.add_argument("-taskfile", type = str, default = "task.tex")
    parser.add_argument("-answerfile", type = str, default = "answer.tex")
    args = parser.parse_args()
    random.seed(args.randseed)
    base = random.choice([2,3,5,7])
    a = generate_random_polynomial(2, base)
    b = generate_random_polynomial(2, base)
    c = generate_random_polynomial(3, base)
    while not is_irreducible(c, base):
        c = generate_random_polynomial(3, base)
    with open(args.taskfile, "w") as taskfile:
        taskfile.write('''\\documentclass{article}
        \\usepackage[utf8]{inputenc}
        \\usepackage[english, russian]{babel}
        \\begin{document}
        Чему равно произведение многочленов $%s$ и $%s$ над полем $Z_%d$ по
        модулю многочлена $%s$?
        \\end{document}''' % (a, b, base, c))
    with open(args.answerfile, "w") as answerfile:
        answerfile.write('''\\documentclass{article}
        \\usepackage[utf8]{inputenc}
        \\usepackage[english, russian]{babel}
        \\begin{document})
        $%s$
        \\end{document}''' % (a * b % c))
