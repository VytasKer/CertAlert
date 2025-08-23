import { Link } from 'react-router-dom';

export default function Footer() {
  return (
    <footer className="footer">
      <span>Webpage is protected and updated in 2025. All rights reserved.</span>
      <span>
        <Link to="/terms-of-service">Terms of Service</Link> | <Link to="/privacy-policy">Privacy Policy</Link> | <Link to="/contact-us">Contact Us</Link>
      </span>
    </footer>
  )
}