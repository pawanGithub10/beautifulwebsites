import { redirect } from 'next/navigation';

export default function HomePage() {
  // Redirect to a demo site (will be configured in next.config.js)
  redirect('/demo-store');
}
