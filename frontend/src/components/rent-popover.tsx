import { Button } from "./ui/button";
import { Popover, PopoverContent, PopoverTrigger } from "./ui/popover";

type RentPopoverProps = {
  rent: 1 | 2 | 3;
  onRentChnge: (value: number) => void;
};

export default function RentPopover({ rent, onRentChnge }: RentPopoverProps) {
  const getRentLabel = (value: number) => {
    switch (value) {
      case 1:
        return "Low";
      case 2:
        return "Medium";
      case 3:
        return "High";
      default:
        return "Low";
    }
  };

  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button variant="ghost" className="w-64 justify-start">
          <DollarSigns count={rent} />
          <span>Rent: {getRentLabel(rent)}</span>
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-[25rem]" align="start">
        <div className="grid gap-4">
          <div className="space-y-2">
            <h4 className="font-medium leading-none">Rent Price</h4>
            <p className="text-sm text-muted-foreground">
              Set your maximum acceptable rent price.
            </p>
          </div>
          <div className="flex gap-2">
            <Button
              variant={rent === 1 ? "default" : "outline"}
              onClick={() => onRentChnge(1)}
              className="flex-1"
            >
              <DollarSigns count={1} />
              <span>Low</span>
            </Button>
            <Button
              variant={rent === 2 ? "default" : "outline"}
              onClick={() => onRentChnge(2)}
              className="flex-1"
            >
              <DollarSigns count={2} />
              <span>Medium</span>
            </Button>
            <Button
              variant={rent === 3 ? "default" : "outline"}
              onClick={() => onRentChnge(3)}
              className="flex-1"
            >
              <DollarSigns count={3} />
              <span>High</span>
            </Button>
          </div>
        </div>
      </PopoverContent>
    </Popover>
  );
}

function DollarSigns({ count }: { count: number }) {
  return <div className="font-mono text-lg">{"£".repeat(count)}</div>;
}
