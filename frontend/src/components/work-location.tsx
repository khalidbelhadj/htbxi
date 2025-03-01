import { Input } from "./ui/input";
import { LngLat } from "@/types";

type Props = {
  setWorkLocation: (workLocation: LngLat) => void;
}
export default function WorkLocation() {
    return (
          <Input
            placeholder="Work location..."
            className="focus-visible:ring-0 focus-within:border-none shadow-none border-none h-full w-[15rem] p-1 !text-lg"
          />
    )
}