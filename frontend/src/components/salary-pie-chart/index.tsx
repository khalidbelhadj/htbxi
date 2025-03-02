"use client";

import { useState } from "react";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { MonthlyExpensesTab } from "./monthly-expenses-tab";
import { ProjectionsTab } from "./projections-tab";
import { DistrictInfoTab } from "./district-info-tab";
import { SalaryPieChartProps } from "./types";
import { districtData } from "./district-data";

export default function SalaryPieChart({ salary }: SalaryPieChartProps) {
  const [pensionContribution, setPensionContribution] = useState(5); // Default 5% pension contribution
  const [isaContribution, setIsaContribution] = useState(5); // Default 5% ISA contribution

  // Fixed rent price based on district average
  const rentPrice = districtData.averageRent;

  return (
    <Tabs defaultValue="expenses" className="h-full overflow-y-auto p-2 w-full">
      <TabsList className="grid w-full grid-cols-3">
        <TabsTrigger value="expenses">Monthly Expenses</TabsTrigger>
        <TabsTrigger value="projections">Projections</TabsTrigger>
        <TabsTrigger value="district">District Info</TabsTrigger>
      </TabsList>

      {/* Monthly Expenses Tab */}
      <MonthlyExpensesTab
        salary={salary}
        pensionContribution={pensionContribution}
        setPensionContribution={setPensionContribution}
        isaContribution={isaContribution}
        setIsaContribution={setIsaContribution}
        rentPrice={rentPrice}
      />

      {/* Projections Tab */}
      <ProjectionsTab
        salary={salary}
        pensionContribution={pensionContribution}
        setPensionContribution={setPensionContribution}
        isaContribution={isaContribution}
        setIsaContribution={setIsaContribution}
      />

      {/* District Info Tab */}
      <DistrictInfoTab rentPrice={rentPrice} />
    </Tabs>
  );
}
