export default function ContactBanner() {
  return (
    <div className="contact-banner" role="note">
      <span className="contact-banner__mark" aria-hidden="true">
        ?
      </span>
      <div>
        <strong>Need to speak with someone?</strong>
        <p>
          For decisions about your plan, funding, or access, contact the NDIA on
          1800 800 110. For provider safety or complaints, contact the NDIS
          Quality and Safeguards Commission on 1800 035 544.
        </p>
      </div>
    </div>
  );
}
