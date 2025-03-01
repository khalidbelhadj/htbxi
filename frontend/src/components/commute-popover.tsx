import { Button } from "./ui/button";
import { Label } from "./ui/label";
import { Popover, PopoverContent, PopoverTrigger } from "./ui/popover";
import { Slider } from "./ui/slider";
import { Car, Train, FootprintsIcon as Walk } from "lucide-react";

type CommutePopoverProps = {
  commuteTime: number;
  transportMode: "walk" | "drive" | "public";
  onCommuteTimeChange: (value: number) => void;
  onTransportModeChange: (mode: "walk" | "drive" | "public") => void;
};

export default function CommutePopover({
  commuteTime,
  transportMode,
  onCommuteTimeChange,
  onTransportModeChange,
}: CommutePopoverProps) {
  const formatTime = (minutes: number) => {
    if (minutes < 60) {
      return `${minutes} minutes`;
    } else {
      return "1 hour";
    }
  };

  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button variant="ghost" className="w-64 justify-start">
          {transportMode === "walk" && <Walk className="h-4 w-4" />}
          {transportMode === "drive" && <Car className="h-4 w-4" />}
          {transportMode === "public" && <Train className="h-4 w-4" />}
          <span>Commute: {formatTime(commuteTime)}</span>
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-80" align="start">
        <div className="grid gap-4">
          <div className="space-y-2">
            <h4 className="font-medium leading-none">Commute Time</h4>
            <p className="text-sm text-muted-foreground">
              Set your maximum acceptable commute time.
            </p>
          </div>
          <div className="flex gap-2">
            <Button
              variant={transportMode === "walk" ? "default" : "outline"}
              size="icon"
              onClick={() => onTransportModeChange("walk")}
            >
              <Walk className="h-4 w-4" />
              <span className="sr-only">Walking</span>
            </Button>
            <Button
              variant={transportMode === "drive" ? "default" : "outline"}
              size="icon"
              onClick={() => onTransportModeChange("drive")}
            >
              <Car className="h-4 w-4" />
              <span className="sr-only">Driving</span>
            </Button>
            <Button
              variant={transportMode === "public" ? "default" : "outline"}
              size="icon"
              onClick={() => onTransportModeChange("public")}
            >
              <Train className="h-4 w-4" />
              <span className="sr-only">Public Transport</span>
            </Button>
          </div>
          <div className="grid gap-4">
            <div className="grid gap-2">
              <div className="flex justify-between">
                <Label htmlFor="commute-time">
                  Time: {formatTime(commuteTime)}
                </Label>
              </div>
              <Slider
                id="commute-time"
                min={5}
                max={60}
                step={5}
                value={[commuteTime]}
                onValueChange={(value) => onCommuteTimeChange(value[0])}
                className="py-4"
              />
              <div className="flex justify-between text-xs text-muted-foreground">
                <span>5 min</span>
                <span>30 min</span>
                <span>1 hour</span>
              </div>
            </div>
          </div>
        </div>
      </PopoverContent>
    </Popover>
  );
}
