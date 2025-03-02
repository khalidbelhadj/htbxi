// District data for the salary pie chart
import {
  DistrictData,
  PropertyPriceData,
  CrimeData,
  TransportData,
  SchoolPerformanceData,
} from "./types";

// District data
export const districtData: DistrictData = {
  name: "Kensington",
  averageRent: 1200,
  ratings: {
    safety: 7.2,
    schools: 8.5,
    transport: 9.1,
    amenities: 8.8,
  },
};

// Property price data
export const propertyPriceData: PropertyPriceData[] = [
  { year: 2018, price: 450000 },
  { year: 2019, price: 470000 },
  { year: 2020, price: 465000 },
  { year: 2021, price: 490000 },
  { year: 2022, price: 520000 },
  { year: 2023, price: 550000 },
  { year: 2024, price: 580000 },
];

// Crime data
export const crimeData: CrimeData[] = [
  { month: "Jan", violent: 45, property: 78, other: 23 },
  { month: "Feb", violent: 42, property: 71, other: 25 },
  { month: "Mar", violent: 48, property: 80, other: 21 },
  { month: "Apr", violent: 50, property: 75, other: 24 },
  { month: "May", violent: 47, property: 72, other: 28 },
  { month: "Jun", violent: 52, property: 68, other: 30 },
];

// Transport data
export const transportData: TransportData[] = [
  { time: "6am", passengers: 1200 },
  { time: "8am", passengers: 3800 },
  { time: "10am", passengers: 2200 },
  { time: "12pm", passengers: 1800 },
  { time: "2pm", passengers: 2000 },
  { time: "4pm", passengers: 2800 },
  { time: "6pm", passengers: 3600 },
  { time: "8pm", passengers: 2400 },
  { time: "10pm", passengers: 1400 },
];

// School performance data
export const schoolPerformanceData: SchoolPerformanceData[] = [
  { year: 2019, primary: 72, secondary: 68 },
  { year: 2020, primary: 74, secondary: 70 },
  { year: 2021, primary: 75, secondary: 72 },
  { year: 2022, primary: 78, secondary: 75 },
  { year: 2023, primary: 80, secondary: 77 },
];
