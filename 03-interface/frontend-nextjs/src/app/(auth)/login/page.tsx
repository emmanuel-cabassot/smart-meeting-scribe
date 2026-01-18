"use client";

import { useState } from "react";
import Link from "next/link";
import { useAuth } from "@/hooks/use-auth";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
    Card,
    CardContent,
    CardDescription,
    CardFooter,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import { Spinner } from "@/components/common/LoadingSpinner";
import { Eye, EyeOff, LogIn } from "lucide-react";

export default function LoginPage() {
    const { login } = useAuth();
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [showPassword, setShowPassword] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);
        setIsLoading(true);

        const result = await login({
            username: email,
            password: password,
        });

        if (!result.success) {
            setError(result.error || "Erreur de connexion");
        }

        setIsLoading(false);
    };

    return (
        <Card className="w-full max-w-md glass-card hover-glow">
            <CardHeader className="text-center">
                <CardTitle className="text-xl">Connexion</CardTitle>
                <CardDescription>
                    Entrez vos identifiants pour accéder à votre espace
                </CardDescription>
            </CardHeader>

            <form onSubmit={handleSubmit}>
                <CardContent className="space-y-4">
                    {/* Email */}
                    <div className="space-y-2">
                        <Label htmlFor="email">Email</Label>
                        <Input
                            id="email"
                            type="email"
                            placeholder="vous@exemple.com"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                            autoComplete="email"
                            disabled={isLoading}
                        />
                    </div>

                    {/* Password */}
                    <div className="space-y-2">
                        <Label htmlFor="password">Mot de passe</Label>
                        <div className="relative">
                            <Input
                                id="password"
                                type={showPassword ? "text" : "password"}
                                placeholder="••••••••"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                                autoComplete="current-password"
                                disabled={isLoading}
                                className="pr-10"
                            />
                            <button
                                type="button"
                                onClick={() => setShowPassword(!showPassword)}
                                className="absolute right-3 top-1/2 -translate-y-1/2 text-text-tertiary hover:text-text-primary transition-colors"
                                tabIndex={-1}
                            >
                                {showPassword ? (
                                    <EyeOff className="h-4 w-4" />
                                ) : (
                                    <Eye className="h-4 w-4" />
                                )}
                            </button>
                        </div>
                    </div>

                    {/* Error message */}
                    {error && (
                        <div className="p-3 rounded-lg bg-accent-error/10 border border-accent-error/30 text-accent-error text-sm">
                            {error}
                        </div>
                    )}
                </CardContent>

                <CardFooter className="flex flex-col gap-4">
                    <Button
                        type="submit"
                        className="w-full"
                        size="lg"
                        disabled={isLoading}
                    >
                        {isLoading ? (
                            <>
                                <Spinner size="sm" />
                                Connexion...
                            </>
                        ) : (
                            <>
                                <LogIn className="h-4 w-4" />
                                Se connecter
                            </>
                        )}
                    </Button>

                    <p className="text-sm text-text-secondary text-center">
                        Pas encore de compte ?{" "}
                        <Link
                            href="/register"
                            className="text-accent-primary hover:underline font-medium"
                        >
                            Créer un compte
                        </Link>
                    </p>
                </CardFooter>
            </form>
        </Card>
    );
}
