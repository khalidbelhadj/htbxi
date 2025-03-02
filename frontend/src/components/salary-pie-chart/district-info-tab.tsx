"use client";

import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { TabsContent } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Home, TrendingUp, Shield, Landmark, Car } from "lucide-react";
import { formatCurrency, getRatingColor } from "./utils";
import {
  districtData,
  propertyPriceData,
  crimeData,
  transportData,
  schoolPerformanceData,
} from "./district-data";

type DistrictInfoTabProps = {
  rentPrice: number;
};

export function DistrictInfoTab({ rentPrice }: DistrictInfoTabProps) {
  return (
    <TabsContent
      value="district"
      className="space-y-4 max-h-[80vh] overflow-y-auto pr-2"
    >
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-2xl font-bold">{districtData.name}</h3>
          <p className="text-sm text-muted-foreground">District Overview</p>
        </div>
        <Badge variant="outline" className="text-sm">
          Average Rent: {formatCurrency(rentPrice)}/month
        </Badge>
      </div>

      {/* District Ratings */}
      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <div
          className={`rounded-lg border p-3 ${getRatingColor(
            districtData.ratings.safety
          )}`}
        >
          <div className="flex items-center gap-2">
            <Shield className="h-4 w-4" />
            <p className="text-sm font-medium">Safety</p>
          </div>
          <p className="mt-1 text-2xl font-bold">
            {districtData.ratings.safety}/10
          </p>
        </div>
        <div
          className={`rounded-lg border p-3 ${getRatingColor(
            districtData.ratings.schools
          )}`}
        >
          <div className="flex items-center gap-2">
            <Landmark className="h-4 w-4" />
            <p className="text-sm font-medium">Schools</p>
          </div>
          <p className="mt-1 text-2xl font-bold">
            {districtData.ratings.schools}/10
          </p>
        </div>
        <div
          className={`rounded-lg border p-3 ${getRatingColor(
            districtData.ratings.transport
          )}`}
        >
          <div className="flex items-center gap-2">
            <Car className="h-4 w-4" />
            <p className="text-sm font-medium">Transport</p>
          </div>
          <p className="mt-1 text-2xl font-bold">
            {districtData.ratings.transport}/10
          </p>
        </div>
        <div
          className={`rounded-lg border p-3 ${getRatingColor(
            districtData.ratings.amenities
          )}`}
        >
          <div className="flex items-center gap-2">
            <Home className="h-4 w-4" />
            <p className="text-sm font-medium">Amenities</p>
          </div>
          <p className="mt-1 text-2xl font-bold">
            {districtData.ratings.amenities}/10
          </p>
        </div>
      </div>

      {/* Property Price Trends */}
      <div className="rounded-lg border p-4">
        <h4 className="mb-4 text-sm font-semibold flex items-center gap-2">
          <TrendingUp className="h-4 w-4" />
          Property Price Trends
        </h4>
        <div className="h-[200px]">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart
              data={propertyPriceData}
              margin={{ top: 5, right: 20, left: 20, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="year" />
              <YAxis tickFormatter={(value) => `£${value / 1000}k`} />
              <Tooltip formatter={(value) => formatCurrency(Number(value))} />
              <Area
                type="monotone"
                dataKey="price"
                name="Average Property Price"
                stroke="#8884d8"
                fill="#8884d8"
                fillOpacity={0.3}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Crime Statistics */}
      <div className="rounded-lg border p-4">
        <h4 className="mb-4 text-sm font-semibold flex items-center gap-2">
          <Shield className="h-4 w-4" />
          Crime Statistics (Last 6 Months)
        </h4>
        <div className="h-[200px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={crimeData}
              margin={{ top: 5, right: 20, left: 20, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar
                dataKey="violent"
                name="Violent Crime"
                fill="#FF8042"
                stackId="a"
              />
              <Bar
                dataKey="property"
                name="Property Crime"
                fill="#FFBB28"
                stackId="a"
              />
              <Bar
                dataKey="other"
                name="Other Crime"
                fill="#00C49F"
                stackId="a"
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Transport Usage */}
      <div className="rounded-lg border p-4">
        <h4 className="mb-4 text-sm font-semibold flex items-center gap-2">
          <Car className="h-4 w-4" />
          Public Transport Usage (Average Weekday)
        </h4>
        <div className="h-[200px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart
              data={transportData}
              margin={{ top: 5, right: 20, left: 20, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis />
              <Tooltip />
              <Line
                type="monotone"
                dataKey="passengers"
                name="Passengers"
                stroke="#0088FE"
                strokeWidth={2}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* School Performance */}
      <div className="rounded-lg border p-4">
        <h4 className="mb-4 text-sm font-semibold flex items-center gap-2">
          <Landmark className="h-4 w-4" />
          School Performance (% Meeting Standards)
        </h4>
        <div className="h-[200px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart
              data={schoolPerformanceData}
              margin={{ top: 5, right: 20, left: 20, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="year" />
              <YAxis domain={[0, 100]} />
              <Tooltip />
              <Legend />
              <Line
                type="monotone"
                dataKey="primary"
                name="Primary Schools"
                stroke="#8884d8"
                strokeWidth={2}
              />
              <Line
                type="monotone"
                dataKey="secondary"
                name="Secondary Schools"
                stroke="#82ca9d"
                strokeWidth={2}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </TabsContent>
  );
}
