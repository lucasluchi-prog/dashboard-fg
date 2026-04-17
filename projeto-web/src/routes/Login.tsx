export default function Login() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-fg-navy p-6">
      <div className="card w-full max-w-md bg-white p-8 text-center">
        <h1 className="text-xl font-semibold text-fg-navy">Dashboard FG</h1>
        <p className="mt-2 text-sm text-fg-navy/70">
          Acesso restrito ao domínio{" "}
          <span className="font-medium">@furtadoguerini.com.br</span>.
        </p>
        <a
          href={`${import.meta.env.VITE_API_BASE || ""}/login`}
          className="btn btn-primary mt-6 w-full"
        >
          Entrar com Google
        </a>
      </div>
    </div>
  );
}
