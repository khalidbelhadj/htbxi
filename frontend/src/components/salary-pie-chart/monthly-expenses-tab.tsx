"use client";

import { useState, useEffect } from "react";
import {
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip as RechartsTooltip,
  Cell,
  Legend,
} from "recharts";
import { Slider } from "@/components/ui/slider";
import { Label } from "@/components/ui/label";
import { AlertCircle } from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { TabsContent } from "@/components/ui/tabs";
import {
  formatCurrency,
  formatPercentage,
  calculateTakeHomeSalary,
  generatePieChartData,
  ISA_ANNUAL_ALLOWANCE,
  COLORS,
} from "./utils";

type MonthlyExpensesTabProps = {
  salary: number;
  pensionContribution: number;
  setPensionContribution: (value: number) => void;
  isaContribution: number;
  setIsaContribution: (value: number) => void;
  rentPrice: number;
};

export function MonthlyExpensesTab({
  salary,
  pensionContribution,
  setPensionContribution,
  isaContribution,
  setIsaContribution,
  rentPrice,
}: MonthlyExpensesTabProps) {
  const [isaWarning, setIsaWarning] = useState(false);

  // Validate ISA contribution against annual allowance
  useEffect(() => {
    const annualIsaContribution = (salary * isaContribution) / 100;
    setIsaWarning(annualIsaContribution > ISA_ANNUAL_ALLOWANCE);
  }, [salary, isaContribution]);

  const { takeHomeSalary, ni, pensionAmount } = calculateTakeHomeSalary(
    salary,
    pensionContribution
  );

  // Monthly values
  const monthlyTakeHome = takeHomeSalary / 12;
  const monthlyNI = ni / 12;
  const monthlyPension = pensionAmount / 12;
  const monthlyIsaContribution = (salary * (isaContribution / 100)) / 12;
  const annualIsaContribution = salary * (isaContribution / 100);

  // Calculate buffer (take-home salary minus rent and ISA)
  const monthlyBuffer = monthlyTakeHome - rentPrice - monthlyIsaContribution;

  // Check if there's enough money left after expenses
  const isEnoughMoney = monthlyBuffer > 0;

  const chartData = generatePieChartData(
    monthlyNI,
    monthlyPension,
    rentPrice,
    monthlyIsaContribution
  );

  return (
    <TabsContent
      value="expenses"
      className="space-y-4 max-h-[80vh] overflow-y-auto pr-2"
    >
      <div className="space-y-2">
        <div className="flex justify-between">
          <Label>
            District Average Monthly Rent: {formatCurrency(rentPrice)}
          </Label>
        </div>
      </div>

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

      <div className="space-y-2">
        <div className="flex justify-between">
          <Label htmlFor="isa-contribution-expenses">
            ISA Contribution: {formatPercentage(isaContribution)}
          </Label>
          <span className="text-xs text-muted-foreground">
            {formatCurrency(annualIsaContribution)}/year
          </span>
        </div>
        <Slider
          id="isa-contribution-expenses"
          min={0}
          max={20}
          step={1}
          value={[isaContribution]}
          onValueChange={(value) => setIsaContribution(value[0])}
          className="py-4"
        />
        <div className="flex justify-between text-xs text-muted-foreground">
          <span>0%</span>
          <span>10%</span>
          <span>20%</span>
        </div>
      </div>

      {isaWarning && (
        <Alert variant="default" className="bg-yellow-50 border-yellow-200">
          <AlertCircle className="h-4 w-4 text-yellow-600" />
          <AlertDescription className="text-yellow-700">
            Your annual ISA contribution of{" "}
            {formatCurrency(annualIsaContribution)} exceeds the annual allowance
            of {formatCurrency(ISA_ANNUAL_ALLOWANCE)}.
          </AlertDescription>
        </Alert>
      )}

      <div className="grid grid-cols-2 gap-4">
        <div className="rounded-lg bg-muted p-3">
          <p className="text-sm font-medium">Annual Salary</p>
          <p className="text-2xl font-bold">{formatCurrency(salary)}</p>
        </div>
        <div className="rounded-lg bg-muted p-3">
          <p className="text-sm font-medium">Monthly Take-Home</p>
          <p className="text-2xl font-bold">
            {formatCurrency(monthlyTakeHome)}
          </p>
        </div>
        <div className="rounded-lg bg-muted p-3">
          <p className="text-sm font-medium">Monthly Buffer</p>
          <p
            className={`text-2xl font-bold ${
              monthlyBuffer < 0 ? "text-red-500" : ""
            }`}
          >
            {formatCurrency(monthlyBuffer)}
          </p>
        </div>
        <div className="rounded-lg bg-muted p-3">
          <p className="text-sm font-medium">Monthly Savings</p>
          <p className="text-2xl font-bold">
            {formatCurrency(monthlyPension + monthlyIsaContribution)}
          </p>
        </div>
      </div>

      {/* Big text showing amount left after bills */}
      <div className="my-6 rounded-lg bg-primary/10 p-4 text-center">
        <p className="text-lg font-medium">After bills, you still have</p>
        <p
          className={`text-3xl font-bold ${
            monthlyBuffer < 0 ? "text-red-500" : "text-primary"
          }`}
        >
          {formatCurrency(monthlyBuffer)}
        </p>
        <p className="text-sm text-muted-foreground">left to spend</p>
      </div>

      {!isEnoughMoney && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            Your expenses exceed your take-home pay. Consider reducing your
            pension or ISA contributions.
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
            <RechartsTooltip
              formatter={(value) => formatCurrency(Number(value))}
            />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </TabsContent>
  );
}
