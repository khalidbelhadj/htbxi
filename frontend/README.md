# Rent Prediction Frontend

This is the frontend for the Rent Prediction application. It uses Next.js, React, and gRPC-Web to communicate with the backend service.

## Setup

1. Install dependencies:
   ```bash
   npm install
   # or
   yarn install
   ```

2. Generate TypeScript code from Proto files:
   ```bash
   npm run generate-proto
   # or
   yarn generate-proto
   ```

3. Start the development server:
   ```bash
   npm run dev
   # or
   yarn dev
   ```

## gRPC Integration

The application uses gRPC-Web to communicate with the backend service. The proto file is located at `src/proto/rent_prediction.proto`.

### Using the Rent Prediction Service

You can use the `predictRent` function from `src/actions.ts` to make predictions:

```typescript
import { predictRent } from "@/actions";

// Example usage
const predictions = await predictRent({
  workLocation: { lat: 51.5074, lng: -0.1278 },
  commuteTimeMinutes: 30,
  commuteType: "drive",
  rentOption: 2
});

// predictions will be an array of RentPrediction objects
// [
//   {
//     district: "SW1",
//     meanRent: 1500,
//     medianRent: 1400,
//     location: {
//       latitude: 51.5074,
//       longitude: -0.1278
//     }
//   },
//   ...
// ]
```

### Proto Schema

The proto schema defines the following:

- `Location`: A message containing latitude and longitude
- `PredictionRequest`: The request message containing work location, commute preferences, and rent options
- `RentPrediction`: A prediction result containing district, rent values, and location
- `PredictionResponse`: The response message containing an array of predictions and any error messages

## Development

To modify the gRPC service:

1. Edit the proto file at `src/proto/rent_prediction.proto`
2. Regenerate the TypeScript code using `yarn generate-proto`
3. Update the `predictRent` function in `src/actions.ts` if necessary

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
