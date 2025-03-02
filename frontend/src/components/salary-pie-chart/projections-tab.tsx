"use client";

import { useState, useEffect } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip as RechartsTooltip,
} from "recharts";
import { Slider } from "@/components/ui/slider";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { Label } from "@/components/ui/label";
import { AlertCircle, InfoIcon } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

import { Alert, AlertDescription } from "@/components/ui/alert";
import { TabsContent } from "@/components/ui/tabs";
import {
  formatCurrency,
  formatPercentage,
  generateProjectionData,
  ISA_ANNUAL_ALLOWANCE,
} from "./utils";

type ProjectionsTabProps = {
  salary: number;
  pensionContribution: number;
  setPensionContribution: (value: number) => void;
  isaContribution: number;
  setIsaContribution: (value: number) => void;
};

export function ProjectionsTab({
  salary,
  pensionContribution,
  setPensionContribution,
  isaContribution,
  setIsaContribution,
}: ProjectionsTabProps) {
  const [isaWarning, setIsaWarning] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);

  // Validate ISA contribution against annual allowance
  useEffect(() => {
    const annualIsaContribution = (salary * isaContribution) / 100;
    setIsaWarning(annualIsaContribution > ISA_ANNUAL_ALLOWANCE);
  }, [salary, isaContribution]);

  // Monthly values
  const monthlyPension = (salary * (pensionContribution / 100)) / 12;
  const monthlyIsaContribution = (salary * (isaContribution / 100)) / 12;
  const annualIsaContribution = salary * (isaContribution / 100);

  const projectionData = generateProjectionData(
    salary,
    pensionContribution,
    isaContribution
  );

  function showDialog(): void {
    setDialogOpen(true);
  }

  return (
    <TabsContent
      value="projections"
      className="space-y-4 max-h-[80vh] overflow-y-auto pr-2"
    >
      <div className="space-y-2">
        <div className="flex justify-between">
          <Label htmlFor="pension-contribution-proj">
            Pension Contribution: {formatPercentage(pensionContribution)}
          </Label>
        </div>
        <Slider
          id="pension-contribution-proj"
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
          <Label htmlFor="isa-contribution-proj">
            ISA Contribution: {formatPercentage(isaContribution)}
          </Label>
          <span className="text-xs text-muted-foreground">
            {formatCurrency(annualIsaContribution)}/year
          </span>
        </div>
        <Slider
          id="isa-contribution-proj"
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

      <div className="grid grid-cols-3 gap-4">
        <div className="rounded-lg bg-muted p-3">
          <p className="text-sm font-medium">Monthly Pension</p>
          <p className="text-2xl font-bold">{formatCurrency(monthlyPension)}</p>
        </div>
        <div className="rounded-lg bg-muted p-3">
          <p className="text-sm font-medium">Monthly ISA</p>
          <p className="text-2xl font-bold">
            {formatCurrency(monthlyIsaContribution)}
          </p>
        </div>
        <div className="rounded-lg bg-muted p-3">
          <p className="text-sm font-medium">Monthly Total</p>
          <p className="text-2xl font-bold">
            {formatCurrency(monthlyPension + monthlyIsaContribution)}
          </p>
        </div>
      </div>

      <div className="my-6 rounded-lg bg-primary/10 p-4 text-center">
        <div className="flex justify-end">
          <Tooltip>
            <TooltipTrigger onClick={() => showDialog()}>
              <InfoIcon className="size-4" />
            </TooltipTrigger>
            <TooltipContent>
              <p>Projection details</p>
            </TooltipContent>
          </Tooltip>
        </div>
        <p className="text-lg font-medium">Projected value after 40 years</p>
        <p className="text-3xl font-bold text-primary">
          {formatCurrency(projectionData[projectionData.length - 1].total)}
        </p>
        <p className="text-sm text-muted-foreground">
          Pension:{" "}
          {formatCurrency(projectionData[projectionData.length - 1].pension)} |
          ISA: {formatCurrency(projectionData[projectionData.length - 1].isa)}
        </p>
      </div>

      <div className="h-[300px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={projectionData.filter(
              (_, index) =>
                index % 5 === 0 || index === projectionData.length - 1
            )}
            margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="year"
              label={{
                value: "Years",
                position: "insideBottomRight",
                offset: -5,
              }}
            />
            <YAxis
              tickFormatter={(value) => `£${(value / 1000).toFixed(0)}k`}
            />
            <RechartsTooltip
              formatter={(value: number) => formatCurrency(value)}
            />
            <Legend />
            <Line
              type="monotone"
              dataKey="pension"
              name="Pension"
              stroke="#FFBB28"
              activeDot={{ r: 8 }}
            />
            <Line
              type="monotone"
              dataKey="isa"
              name="ISA"
              stroke="#00C49F"
              activeDot={{ r: 8 }}
            />
            <Line
              type="monotone"
              dataKey="total"
              name="Total"
              stroke="#0088FE"
              strokeWidth={2}
              activeDot={{ r: 8 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Projection Calculation Details</DialogTitle>
            <DialogDescription>
              How your investment projections are calculated
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 mt-4">
            <div className="space-y-2">
              <h3 className="font-medium">Assumptions</h3>
              <ul className="list-disc pl-5 space-y-1 text-sm">
                <li>
                  Projection period:{" "}
                  <span className="font-medium">40 years</span>
                </li>
                <li>
                  Pension annual growth rate:{" "}
                  <span className="font-medium">5%</span>
                </li>
                <li>
                  ISA annual growth rate:{" "}
                  <span className="font-medium">4%</span>
                </li>
                <li>
                  Annual pension contribution:{" "}
                  <span className="font-medium">
                    {formatCurrency((salary * pensionContribution) / 100)}
                  </span>{" "}
                  ({formatPercentage(pensionContribution)} of salary)
                </li>
                <li>
                  Annual ISA contribution:{" "}
                  <span className="font-medium">
                    {formatCurrency((salary * isaContribution) / 100)}
                  </span>{" "}
                  ({formatPercentage(isaContribution)} of salary)
                </li>
              </ul>
            </div>

            <div className="space-y-2">
              <h3 className="font-medium">Calculation Method</h3>
              <p className="text-sm text-muted-foreground">
                For each year in the projection period:
              </p>
              <ol className="list-decimal pl-5 space-y-1 text-sm">
                <li>
                  Annual contributions are added to both pension and ISA totals
                </li>
                <li>Growth rates are applied to the accumulated totals</li>
                <li>Pension total grows at 5% per year</li>
                <li>ISA total grows at 4% per year</li>
                <li>The combined total is the sum of pension and ISA values</li>
              </ol>
            </div>

            <div className="space-y-2">
              <h3 className="font-medium">Important Notes</h3>
              <ul className="list-disc pl-5 space-y-1 text-sm text-muted-foreground">
                <li>
                  These projections are estimates based on consistent
                  contributions and growth rates
                </li>
                <li>
                  Actual returns may vary based on market conditions and
                  investment choices
                </li>
                <li>
                  The model does not account for inflation, which will reduce
                  the real value of your savings
                </li>
                <li>Tax rules and allowances may change over time</li>
              </ul>
            </div>

            <div className="bg-muted p-4 rounded-md">
              <h3 className="font-medium mb-2">
                Final Projected Values (After 40 Years)
              </h3>
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <p className="text-sm font-medium">Pension</p>
                  <p className="text-lg font-bold">
                    {formatCurrency(
                      projectionData[projectionData.length - 1].pension
                    )}
                  </p>
                </div>
                <div>
                  <p className="text-sm font-medium">ISA</p>
                  <p className="text-lg font-bold">
                    {formatCurrency(
                      projectionData[projectionData.length - 1].isa
                    )}
                  </p>
                </div>
                <div>
                  <p className="text-sm font-medium">Total</p>
                  <p className="text-lg font-bold text-primary">
                    {formatCurrency(
                      projectionData[projectionData.length - 1].total
                    )}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </TabsContent>
  );
}
