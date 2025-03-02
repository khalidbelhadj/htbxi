"use client";

import { useState } from "react";
import {
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  Cell,
  Legend,
} from "recharts";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Slider } from "@/components/ui/slider";
import { Label } from "@/components/ui/label";
import { AlertCircle } from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";

type SalaryPieChartProps = {
  salary: number;
};

export default function SalaryPieChart({ salary }: SalaryPieChartProps) {
  const [pensionContribution, setPensionContribution] = useState(5); // Default 5% pension contribution

  // Calculate mock data based on salary
  const monthlyIncome = salary / 12;

  // Calculate tax (simplified UK tax calculation)
  const calculateTax = (annualSalary: number, pensionPercentage: number) => {
    // Pension contribution is tax-free
    const pensionAmount = annualSalary * (pensionPercentage / 100);
    const taxableAmount = annualSalary - pensionAmount;

    // Basic tax calculation (simplified)
    let tax = 0;

    // Personal allowance
    const personalAllowance = 12570;

    // Taxable income
    let taxableIncome = Math.max(0, taxableAmount - personalAllowance);

    // Basic rate: 20% on income between £12,571 and £50,270
    if (taxableIncome > 0) {
      const basicRateAmount = Math.min(taxableIncome, 50270 - 12571);
      tax += basicRateAmount * 0.2;
      taxableIncome -= basicRateAmount;
    }

    // Higher rate: 40% on income between £50,271 and £125,140
    if (taxableIncome > 0) {
      const higherRateAmount = Math.min(taxableIncome, 125140 - 50271);
      tax += higherRateAmount * 0.4;
      taxableIncome -= higherRateAmount;
    }

    // Additional rate: 45% on income over £125,140
    if (taxableIncome > 0) {
      tax += taxableIncome * 0.45;
    }

    return tax;
  };

  const annualTax = calculateTax(salary, pensionContribution);
  const monthlyTax = annualTax / 12;

  // National Insurance (simplified)
  const calculateNI = (annualSalary: number) => {
    // Simplified NI calculation
    if (annualSalary <= 12570) return 0;

    const niThreshold = 12570;
    const niUpperLimit = 50270;

    let ni = 0;

    // 12% on income between threshold and upper limit
    if (annualSalary > niThreshold) {
      const lowerBand = Math.min(annualSalary, niUpperLimit) - niThreshold;
      ni += lowerBand * 0.12;
    }

    // 2% on income above upper limit
    if (annualSalary > niUpperLimit) {
      ni += (annualSalary - niUpperLimit) * 0.02;
    }

    return ni;
  };

  const annualNI = calculateNI(salary);
  const monthlyNI = annualNI / 12;

  // Pension contribution
  const monthlyPension = (salary * (pensionContribution / 100)) / 12;

  // Rent (mock data - 30% of after-tax income)
  const afterTaxMonthly =
    monthlyIncome - monthlyTax - monthlyNI - monthlyPension;

  // Check if there's enough money left after pension contribution
  const isEnoughMoney = afterTaxMonthly > 0;

  // Calculate expenses based on after-tax income
  const rent = afterTaxMonthly * 0.3;
  const food = afterTaxMonthly * 0.15;
  const transport = afterTaxMonthly * 0.1;
  const utilities = afterTaxMonthly * 0.08;
  const entertainment = afterTaxMonthly * 0.07;
  const savings = afterTaxMonthly * 0.2;
  const other =
    afterTaxMonthly -
    rent -
    food -
    transport -
    utilities -
    entertainment -
    savings;

  const COLORS = [
    "#0088FE", // Tax
    "#00C49F", // National Insurance
    "#9C27B0", // Pension
    "#FFBB28", // Rent
    "#FF8042", // Food
    "#A28DFF", // Transport
    "#FF6B6B", // Utilities
    "#4ECDC4", // Entertainment
    "#C7F464", // Savings
    "#81D4FA", // Other
  ];

  const chartData = [
    { name: "Tax", value: Math.round(monthlyTax) },
    { name: "National Insurance", value: Math.round(monthlyNI) },
    { name: "Pension", value: Math.round(monthlyPension) },
    { name: "Rent", value: Math.round(rent) },
    { name: "Food", value: Math.round(food) },
    { name: "Transport", value: Math.round(transport) },
    { name: "Utilities", value: Math.round(utilities) },
    { name: "Entertainment", value: Math.round(entertainment) },
    { name: "Savings", value: Math.round(savings) },
    { name: "Other", value: Math.round(other) },
  ];

  const formatCurrency = (value: number) => {
    return `£${value.toLocaleString()}`;
  };

  const formatPercentage = (value: number) => {
    return `${value}%`;
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Monthly Expenses</CardTitle>
        <CardDescription>
          Breakdown of your monthly income and expenses
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="space-y-2">
            <div className="flex justify-between">
              <Label htmlFor="pension-contribution">
                Pension Contribution: {formatPercentage(pensionContribution)}
              </Label>
            </div>
            <Slider
              id="pension-contribution"
              min={0}
              max={50}
              step={1}
              value={[pensionContribution]}
              onValueChange={(value) => setPensionContribution(value[0])}
              className="py-4"
            />
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>0%</span>
              <span>25%</span>
              <span>50%</span>
            </div>
          </div>

          {!isEnoughMoney && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                Pension contribution is too high. Not enough money left for
                expenses.
              </AlertDescription>
            </Alert>
          )}

          <div className="h-[250px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={chartData}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  labelLine={false}
                >
                  {chartData.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={COLORS[index % COLORS.length]}
                    />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => formatCurrency(Number(value))} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
