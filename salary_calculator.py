from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import List


import logging
import argparse
import sys


@dataclass
class DeductionCalculator(ABC):
    @abstractmethod
    def calculate(self, gross_salary):
        pass


@dataclass
class TaxBracket:
    max_taxable_income: int
    tax_rate: float


@dataclass
class TaxBracketsDeductionCalculator(DeductionCalculator):
    tax_brackets: List[TaxBracket]

    def calculate(self, gross_salary):
        deduction = 0

        last_max_taxable_income = 0
        for tax_bracket in self.tax_brackets:
            if gross_salary >= last_max_taxable_income:
                bracket_taxable_income = min(gross_salary, tax_bracket.max_taxable_income) - last_max_taxable_income
                bracket_tax_deduction = bracket_taxable_income * tax_bracket.tax_rate
                deduction += bracket_tax_deduction

                last_max_taxable_income = tax_bracket.max_taxable_income
            else:
                break

        return deduction


@dataclass
class IncomeTaxCalculator(DeductionCalculator):
    TAX_POINT_VALUE = 223

    tax_points: float
    tax_brackets_deduction_calculator: TaxBracketsDeductionCalculator = TaxBracketsDeductionCalculator([TaxBracket(6450, 0.1),
                                                                                                        TaxBracket(9240, 0.14),
                                                                                                        TaxBracket(14840, 0.2),
                                                                                                        TaxBracket(20620, 0.31),
                                                                                                        TaxBracket(42910, 0.35),
                                                                                                        TaxBracket(55270, 0.47),
                                                                                                        TaxBracket(sys.maxsize, 0.5)])

    def calculate(self, gross_salary):
        return self.tax_brackets_deduction_calculator.calculate(gross_salary) - IncomeTaxCalculator.TAX_POINT_VALUE * self.tax_points


    def __repr__(self):
        return "Income tax"


@dataclass
class NationalInsuranceCalculator(DeductionCalculator):
    tax_brackets_deduction_calculator: TaxBracketsDeductionCalculator = TaxBracketsDeductionCalculator([TaxBracket(6331, 0.004),
                                                                                                        TaxBracket(44020, 0.07)])

    def calculate(self, gross_salary):
        return self.tax_brackets_deduction_calculator.calculate(gross_salary)


    def __repr__(self):
        return "National insurance"


@dataclass
class HealthInsuranceCalculator(DeductionCalculator):
    tax_brackets_deduction_calculator: TaxBracketsDeductionCalculator = TaxBracketsDeductionCalculator([TaxBracket(6331, 0.031),
                                                                                                        TaxBracket(44020, 0.05)])

    def calculate(self, gross_salary):
        return self.tax_brackets_deduction_calculator.calculate(gross_salary)


    def __repr__(self):
        return "Health insurance"

@dataclass
class MandatoryPensionSavingsCalculator(DeductionCalculator):
    def calculate(self, gross_salary):
        return gross_salary * 0.06


    def __repr__(self):
        return "Mandatory pension savings"


@dataclass
class NetSalaryCalculator:
    deduction_calculators: List[DeductionCalculator]

    def calculate(self, gross_salary):
        deductions = 0
        for deduction_calculator in self.deduction_calculators:
            deduction = deduction_calculator.calculate(gross_salary)
            deductions += deduction
            logging.debug(f'{deduction_calculator}: {deduction:.2f}')

        return gross_salary - deductions


class NetSalaryCalculatorFactory:
    def create(self, tax_points):
        deduction_calculators = [IncomeTaxCalculator(tax_points),
                                 NationalInsuranceCalculator(),
                                 HealthInsuranceCalculator(),
                                 MandatoryPensionSavingsCalculator()]

        return NetSalaryCalculator(deduction_calculators)


def main():
    initialize_logger()
    args = parse_args()
    gross_salary = args.gross_salary
    tax_points = args.tax_points

    net_salary_calculator_factory = NetSalaryCalculatorFactory()
    net_salary_calculator = net_salary_calculator_factory.create(tax_points)
    
    net_salary = net_salary_calculator.calculate(gross_salary)
    logging.info('------------------------------------')
    logging.info(f'Net salary: {net_salary:.2f}')


def initialize_logger():
    logging.basicConfig(format='%(message)s', level=logging.DEBUG)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--gross_salary', type=int, help='Gross salary', required=True)
    parser.add_argument('--tax_points', type=float, help='Gross salary', required=False, default=2.25)

    return parser.parse_args()


if __name__ == '__main__':
    main()
