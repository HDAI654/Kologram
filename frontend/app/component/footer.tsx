function Footer() {
    return (
        <>
            {/* Main Footer */}
            <hr className="w-100" />
            <div className="container">
                {/* Brand Logo */} 
                <div className="row justify-content-center align-items-center">
                    <svg
                    aria-hidden="true"
                    focusable="false"
                    viewBox="0 0 24 24"
                    role="img"
                    width="90px"
                    height="90px"
                    fill="none"
                    className="mb-5"
                    >
                        <path
                        fill="currentColor"
                        d="M4 13c1.5 3 4.5 4.5 8 4.5s6.5-1.5 8-4.5c.2-.4.2-.8-.1-1.1-.3-.3-.8-.3-1.1 0-1.2 2.5-3.7 3.6-6.8 3.6s-5.6-1.1-6.8-3.6c-.2-.4-.7-.5-1.1-.2-.3.3-.4.7-.1 1.1z"
                        />
                    </svg>
                </div>

                <footer className="py-5">
                    <div className="row">
                        <div className="col-6 col-md-2 mb-3">
                            <h5>Section</h5>
                            <ul className="nav flex-column">
                                <li className="nav-item mb-2">
                                <a href="/" className="nav-link p-0 text-body-secondary">Home</a>
                                </li>
                                <li className="nav-item mb-2">
                                <a href="/reg_banner" className="nav-link p-0 text-body-secondary">Register banner</a>
                                </li>
                                <li className="nav-item mb-2">
                                <a href="/rules" className="nav-link p-0 text-body-secondary">Site Rules</a>
                                </li>
                                <li className="nav-item mb-2">
                                <a href="/faqs" className="nav-link p-0 text-body-secondary">FAQs</a>
                                </li>
                                <li className="nav-item mb-2">
                                <a href="/about" className="nav-link p-0 text-body-secondary">About</a>
                                </li>
                            </ul>
                        </div>

                        {/* Collect Emails form */}
                        <div className="col-md-5 offset-md-1 mb-3">
                            <form>
                                <h5>Subscribe to our newsletter</h5>
                                <p>Monthly digest of what's new and exciting from us.</p>
                                <div className="d-flex flex-column flex-sm-row w-100">
                                    <label htmlFor="newsletter1" className="visually-hidden">Email address</label>
                                    <input
                                    id="newsletter1"
                                    type="email"
                                    className="form-control"
                                    placeholder="Email address"
                                    />
                                    <button className="btn btn-primary " type="button">
                                    Subscribe
                                    </button>
                                </div>
                            </form>
                        </div>
                    </div>
                    
                    {/* Contact Information */}
                    <div className="container py-4 border-top">
                        <div className="row align-items-center">
                            <div className="col-md-6 text-center text-md-start mb-3 mb-md-0">
                                <p className="mb-0">© 2025 Company, Inc. All rights reserved.</p>
                            </div>

                            <div className="col-md-6">
                                <div className="d-flex justify-content-center justify-content-md-end align-items-center gap-3 flex-wrap">

                                    {/* Telegram */}
                                    <a className="h5" href="https://t.me/yourtelegram" target="_blank" rel="noopener noreferrer" aria-label="Telegram">
                                        <i className="fab fa-telegram fa-lg"></i>
                                    </a>

                                    {/* Facebook */}
                                    <a className="h5" href="https://facebook.com/yourpage" target="_blank" rel="noopener noreferrer" aria-label="Facebook">
                                        <i className="fab fa-facebook fa-lg"></i>
                                    </a>

                                    {/* GitHub */}
                                    <a className="h5" href="https://github.com/HDAI654" target="_blank" rel="noopener noreferrer" aria-label="GitHub">
                                        <i className="fab fa-github fa-lg"></i>
                                    </a>

                                    {/* Gmail */}
                                    <a className="h5 d-flex align-items-center gap-1" href="mailto:hdai.code@gmail.com" aria-label="Gmail">
                                        <i className="fas fa-envelope fa-lg"></i>
                                        <span className="d-none d-sm-inline">hdai.code@gmail.com</span>
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>
                </footer>
            </div>
        </>
        
    );
}

export default Footer;
