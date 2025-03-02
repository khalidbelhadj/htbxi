// Types for the salary pie chart components

export type SalaryPieChartProps = {
  salary: number;
};

export type DistrictData = {
  name: string;
  averageRent: number;
  ratings: {
    safety: number;
    schools: number;
    transport: number;
    amenities: number;
  };
};

// Chart data types
export type PropertyPriceData = {
  year: number;
  price: number;
};

export type CrimeData = {
  month: string;
  violent: number;
  property: number;
  other: number;
};

export type TransportData = {
  time: string;
  passengers: number;
};

export type SchoolPerformanceData = {
  year: number;
  primary: number;
  secondary: number;
};

export type ProjectionData = {
  year: number;
  pension: number;
  isa: number;
  total: number;
};

export type PieChartData = {
  name: string;
  value: number;
};
