from math import factorial


def count_k(sequence):
    """
    Подсчитывает число информационных разрядов (длина)
    :param sequence: число (инф. последовательность)
    :return: число разрядов
    """
    if type(sequence) == int:
        sequence = bin(sequence)[2:]
    return len(sequence)


def count_power(polynomial):
    """
    Возвращает степень образующего полинома
    :param polynomial: полином
    :return: его степень
    """
    return count_k(polynomial) - 1


def count_nonzero_bits(number):
    """
    Считает количество ненулевых битов в числе:
    например, при number = 00110100 ненулевых битов 3
    :param number:
    :return: bit_count - количество ненулевых битов
    """
    bit_count = 0
    while number != 0b0:
        bit = number & 0b1
        if bit == 0b1:
            bit_count += 1

        number >>= 1

    return bit_count


def divide_with_xor(dividend: int, divisor: int):
    """
    Делит делимое на делитель, вместо вычитания – XOR (сложение по модулю 2)
    :param dividend: делимое
    :param divisor: делитель
    :return: частное, остаток
    """
    dividend_digit_count = count_k(dividend)
    divisor_digit_count = count_k(divisor)
    if dividend_digit_count < divisor_digit_count:
        return 0, dividend
    i = dividend_digit_count - divisor_digit_count + 1  # итерации
    quotient = 0  # частное
    remainder = 0  # остаток
    part = dividend >> i - 1
    while i > 0:
        i -= 1

        quotient <<= 1
        if count_k(part) >= divisor_digit_count:
            quotient += 1
            part ^= divisor
        else:
            quotient += 0

        if i == 0:
            remainder = part
        else:
            next_digit = (dividend >> (i - 1)) & 0b1
            part <<= 1
            part += next_digit

    return quotient, remainder


def encrypt_with_cyclic_code(sequence, g, k, n):
    """
    Кодирует принципами циклического кода инф. последовательность
    :param sequence: число (инф. последовательность)
    :param g: образующий полином
    :param k: число информационных разрядов (длина)
    :param n: степень образующего полинома + k
    :return: закодированная инф. последовательность
    """
    # 1. умножаем полином инф. посл-ти на x^(n-k)
    # фактически выполняем сдвиг влево
    shifted = sequence + '0' * (n - k)
    print('x^(n-k)*m(x) =', shifted)

    # 2. вычисляем остаток от деления получившегося полинома на g(x)
    mod = divide_with_xor(int(shifted, 2), int(g, 2))[1]
    print('x^(n-k)*m(x) mod (with xor) g(x) =', bin(mod)[2:])

    # 3. 1010000 + 11 = конкатенация 1010 и 011
    mod_len = len(bin(mod)[2:])
    return seq + '0' * (n - k - mod_len) + bin(mod)[2:]


def count_number_of_combination(k, n):
    """
    Число сочетаний из n по k
    :param k: k
    :param n: n
    :return: Число сочетаний из n по k
    """
    assert n >= k
    return factorial(n) / (factorial(k) * (factorial(n - k)))


def count_co(encoded: int, g: int, n: int):
    """
    Рассчитывает обнаруживающую способность, возвращает массив, где
    индекс – i - кратность ошибки,
    элементы - словари – ключ:
        C(i,n) – число сочетаний из n по i
        No – кол-во обнаруженных ошибок
        Co – обнаруживающая способность – отношение No к C(i,n)
    :param encoded: переданная инф. посл-ть v(x)
    :param g: образующий полином
    :param n: длина кодовой комбинации
    :return: таблица
    """
    # результат Co по i – количество ошибочных битов
    result = [{'C(i,n)': 0, 'No': 0, 'Co': 0.0} for _ in range(n + 1)]
    assert divide_with_xor(encoded, g)[1] == 0, 'Вектор ошибок не наложен, ' \
                                                'но вектор синдрома не нулевой'
    result[0]['No'] = 0

    # перебираем все возможные вектора ошибок
    for error_vector in range(0b1, 0b1 << n):  # от 0000001 до 1111111
        # принятый полином r(x)
        received = encoded ^ error_vector

        got_syndrome_vector = divide_with_xor(received, g)[1]
        if got_syndrome_vector != 0:
            result[count_nonzero_bits(error_vector)]['No'] += 1

    for i in range(n + 1):
        result[i]['C(i,n)'] = int(count_number_of_combination(i, n))

    for i in range(n + 1):
        result[i]['Co'] = result[i]['No'] / result[i]['C(i,n)'] * 100

    return result


if __name__ == '__main__':
    # информационная последовательность 1010
    # seq = '0010'
    seq = '1010'
    print('Информационная последовательность =', seq)

    # k – число информационных разрядов данной последовательности
    k = count_k(seq)  # 4

    # g(x) = x^3 + x + 1 – образующий полином, в двоичном формате: 1011
    g = '1011'
    print('Образующий полином =', g)
    # r - степень образующего полинома
    r = count_power(g)  # 3

    # => n = r + k = 3 + 4 = 7
    n = r + k  # 7

    # таблица вектора синдрома s(x) -> ошибка e(x)
    # syndrome_table = [0] * 8
    # syndrome_table[0b000] = 0b0000000
    # syndrome_table[0b001] = 0b0000001
    # syndrome_table[0b010] = 0b0000010
    # syndrome_table[0b100] = 0b0000100
    # syndrome_table[0b011] = 0b0001000
    # syndrome_table[0b110] = 0b0010000
    # syndrome_table[0b111] = 0b0100000
    # syndrome_table[0b101] = 0b1000000

    encoded = encrypt_with_cyclic_code(seq, g, k, n)  # v(x) - передаем
    print('Кодовое слово =', encoded)
    result_table = count_co(int(encoded, 2), int(g, 2), n)
    for i, metrics in enumerate(result_table):
        print(i, metrics)
