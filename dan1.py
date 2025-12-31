class Term:
    def __init__(self, coef, exp):
        self.coef = coef
        self.exp = exp

    def __str__(self):
        if self.exp == 0:
            return f"{self.coef}"
        elif self.exp == 1:
            return f"{self.coef}x"
        else:
            return f"{self.coef}x^{self.exp}"


class Polynomial:
    def __init__(self):
        self.terms = []  # List of Term

    def add_term(self, coef, exp):
        for term in self.terms:
            if term.exp == exp:
                term.coef += coef
                return
        self.terms.append(Term(coef, exp))
        self.terms.sort(key=lambda t: -t.exp)

    def add_polynomial(self, other):
        result = Polynomial()
        for term in self.terms:
            result.add_term(term.coef, term.exp)
        for term in other.terms:
            result.add_term(term.coef, term.exp)
        return result

    def subtract_polynomial(self, other):
        result = Polynomial()
        for term in self.terms:
            result.add_term(term.coef, term.exp)
        for term in other.terms:
            result.add_term(-term.coef, term.exp)
        return result

    def __str__(self):
        if not self.terms:
            return "0"
        return " + ".join(str(term) for term in self.terms)


def subtract_polynomial(p1, p2):
    return p1.subtract_polynomial(p2)


class PolynomialMenu:
    def __init__(self):
        self.polynomials = []

    def input_polynomial(self):
        print("\n=== Nhập đa thức mới ===")
        poly = Polynomial()
        n = int(input("Nhập số lượng hạng tử của đa thức: "))
        for i in range(n):
            coef = float(input(f"  Hệ số của hạng tử #{i + 1}: "))
            exp = int(input(f"  Số mũ của hạng tử #{i + 1}: "))
            poly.add_term(coef, exp)
        self.polynomials.append(poly)
        print("✅ Đa thức đã được thêm.")

    def show_polynomials(self):
        if not self.polynomials:
            print("❌ Chưa có đa thức nào được nhập.")
        else:
            print("\n=== Danh sách đa thức ===")
            for i, poly in enumerate(self.polynomials):
                print(f"[{i}] P{i}(x) = {poly}")

    def add_two_polynomials(self):
        self.show_polynomials()
        try:
            i = int(input("Chọn chỉ số của đa thức thứ 1: "))
            j = int(input("Chọn chỉ số của đa thức thứ 2: "))
            if i < 0 or j < 0 or i >= len(self.polynomials) or j >= len(self.polynomials):
                print("❌ Chỉ số không hợp lệ.")
                return
            result = self.polynomials[i].add_polynomial(self.polynomials[j])
            print(f"\n✅ Kết quả cộng P{i}(x) + P{j}(x): {result}")
        except Exception as e:
            print(f"Lỗi: {e}")

    def subtract_two_polynomials(self):
        self.show_polynomials()
        try:
            i = int(input("Chọn chỉ số của đa thức bị trừ (P1): "))
            j = int(input("Chọn chỉ số của đa thức trừ (P2): "))
            if i < 0 or j < 0 or i >= len(self.polynomials) or j >= len(self.polynomials):
                print("❌ Chỉ số không hợp lệ.")
                return
            result = subtract_polynomial(self.polynomials[i], self.polynomials[j])
            print(f"\n✅ Kết quả trừ P{i}(x) - P{j}(x): {result}")
        except Exception as e:
            print(f"Lỗi: {e}")

    def menu(self):
        while True:
            print("\n===== MENU =====")
            print("1. Nhập đa thức")
            print("2. Hiển thị tất cả đa thức")
            print("3. Cộng hai đa thức")
            print("4. Trừ hai đa thức")
            print("0. Thoát")
            choice = input("Chọn chức năng: ")

            if choice == "1":
                self.input_polynomial()
            elif choice == "2":
                self.show_polynomials()
            elif choice == "3":
                self.add_two_polynomials()
            elif choice == "4":
                self.subtract_two_polynomials()
            elif choice == "0":
                print("👋 Thoát chương trình.")
                break
            else:
                print("❌ Lựa chọn không hợp lệ. Vui lòng thử lại.")


# Nếu bạn muốn chạy thử menu trong môi trường không tương tác, bỏ comment dòng dưới
# PolynomialMenu().menu()
