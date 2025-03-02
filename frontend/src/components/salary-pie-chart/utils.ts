// Utility functions for the salary pie chart components
import { ProjectionData, PieChartData } from "./types";

// Constants
export const ISA_ANNUAL_ALLOWANCE = 20000;
export const COLORS = [
  "#00C49F", // National Insurance
  "#FFBB28", // Pension
  "#FF8042", // Rent
  "#8884d8", // ISA
];

// Formatting functions
export const formatCurrency = (value: number): string => {
  return `£${value.toLocaleString()}`;
};

export const formatPercentage = (value: number): string => {
  return `${value}%`;
};

export const getRatingColor = (rating: number): string => {
  if (rating >= 8) return "bg-green-100 text-green-800 border-green-300";
  if (rating >= 6) return "bg-yellow-100 text-yellow-800 border-yellow-300";
  return "bg-red-100 text-red-800 border-red-300";
};

// Tax calculation functions
export const calculateTakeHomeSalary = (
  annualSalary: number,
  pensionPercentage: number
) => {
  // Pension contribution is tax-free
  const pensionAmount = annualSalary * (pensionPercentage / 100);
  const taxableAmount = annualSalary - pensionAmount;

  // Tax calculation based on 2024/2025 England tax brackets
  let tax = 0;

  // Personal allowance - £12,570 per year
  const personalAllowance = 12570;

  // Taxable income
  let taxableIncome = Math.max(0, taxableAmount - personalAllowance);

  // Basic rate: 20% on income between £12,571 and £50,270 (up to £37,700 above personal allowance)
  if (taxableIncome > 0) {
    const basicRateAmount = Math.min(taxableIncome, 37700);
    tax += basicRateAmount * 0.2;
    taxableIncome -= basicRateAmount;
  }

  // Higher rate: 40% on income between £50,271 and £125,140
  if (taxableIncome > 0) {
    const higherRateAmount = Math.min(taxableIncome, 125140 - 50270);
    tax += higherRateAmount * 0.4;
    taxableIncome -= higherRateAmount;
  }

  // Additional rate: 45% on income over £125,140
  if (taxableIncome > 0) {
    tax += taxableIncome * 0.45;
  }

  // National Insurance calculation based on 2024/2025 rates
  let ni = 0;

  // Primary threshold - £12,570 per year
  const primaryThreshold = 12570;

  // Upper earnings limit - £50,270 per year
  const upperEarningsLimit = 50270;

  // 8% on earnings between primary threshold and upper earnings limit
  if (annualSalary > primaryThreshold) {
    const lowerBand =
      Math.min(annualSalary, upperEarningsLimit) - primaryThreshold;
    ni += lowerBand * 0.08;
  }

  // 2% on earnings above upper earnings limit
  if (annualSalary > upperEarningsLimit) {
    ni += (annualSalary - upperEarningsLimit) * 0.02;
  }

  // Calculate take-home salary
  const takeHomeSalary = annualSalary - tax - ni - pensionAmount;

  return {
    takeHomeSalary,
    tax,
    ni,
    pensionAmount,
  };
};

// Generate projection data for pension and ISA
export const generateProjectionData = (
  salary: number,
  pensionContribution: number,
  isaContribution: number
): ProjectionData[] => {
  const years = 40; // Project for 40 years
  const annualPensionContribution = (salary * pensionContribution) / 100;
  const annualIsaContribution = (salary * isaContribution) / 100;
  const pensionGrowthRate = 0.05; // 5% annual growth
  const isaGrowthRate = 0.04; // 4% annual growth

  const projectionData = [];
  let pensionTotal = 0;
  let isaTotal = 0;

  for (let year = 0; year <= years; year++) {
    // Add annual contribution
    pensionTotal += annualPensionContribution;
    isaTotal += annualIsaContribution;

    // Apply growth (except for year 0)
    if (year > 0) {
      pensionTotal *= 1 + pensionGrowthRate;
      isaTotal *= 1 + isaGrowthRate;
    }

    projectionData.push({
      year,
      pension: Math.round(pensionTotal),
      isa: Math.round(isaTotal),
      total: Math.round(pensionTotal + isaTotal),
    });
  }

  return projectionData;
};

// Generate pie chart data
export const generatePieChartData = (
  monthlyNI: number,
  monthlyPension: number,
  rentPrice: number,
  monthlyIsaContribution: number
): PieChartData[] => {
  return [
    { name: "National Insurance", value: Math.round(monthlyNI) },
    { name: "Pension", value: Math.round(monthlyPension) },
    { name: "Rent", value: Math.round(rentPrice) },
    { name: "ISA", value: Math.round(monthlyIsaContribution) },
  ];
};
