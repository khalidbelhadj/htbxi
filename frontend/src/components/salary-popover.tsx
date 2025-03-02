import { Button } from "./ui/button";
import { Label } from "./ui/label";
import { Popover, PopoverContent, PopoverTrigger } from "./ui/popover";
import { Slider } from "./ui/slider";
import { PoundSterling } from "lucide-react";

type SalaryPopoverProps = {
  salary: number;
  onSalaryChange: (value: number) => void;
};

export default function SalaryPopover({
  salary,
  onSalaryChange,
}: SalaryPopoverProps) {
  const formatSalary = (amount: number) => {
    return `£${amount.toLocaleString()}`;
  };

  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button variant="ghost" className="w-64 justify-start">
          <PoundSterling className="h-4 w-4" />
          <span>Salary: {formatSalary(salary)}</span>
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-80" align="start">
        <div className="grid gap-4">
          <div className="space-y-2">
            <h4 className="font-medium leading-none">Annual Salary</h4>
            <p className="text-sm text-muted-foreground">
              Set your annual salary for affordability calculations.
            </p>
          </div>
          <div className="grid gap-4">
            <div className="grid gap-2">
              <div className="flex justify-between">
                <Label htmlFor="salary-amount">
                  Amount: {formatSalary(salary)}
                </Label>
              </div>
              <Slider
                id="salary-amount"
                min={20000}
                max={200000}
                step={5000}
                value={[salary]}
                onValueChange={(value) => onSalaryChange(value[0])}
                className="py-4"
              />
              <div className="flex justify-between text-xs text-muted-foreground">
                <span>£20k</span>
                <span>£100k</span>
                <span>£200k</span>
              </div>
            </div>
          </div>
        </div>
      </PopoverContent>
    </Popover>
  );
}
