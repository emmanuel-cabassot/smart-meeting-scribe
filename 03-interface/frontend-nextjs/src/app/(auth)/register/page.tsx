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
import { Eye, EyeOff, UserPlus } from "lucide-react";

export default function RegisterPage() {
    const { register } = useAuth();
    const [fullName, setFullName] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [showPassword, setShowPassword] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);

        // Validation
        if (password.length < 8) {
            setError("Le mot de passe doit contenir au moins 8 caractères");
            return;
        }

        if (password !== confirmPassword) {
            setError("Les mots de passe ne correspondent pas");
            return;
        }

        setIsLoading(true);

        const result = await register({
            email,
            password,
            full_name: fullName || undefined,
        });

        if (!result.success) {
            setError(result.error || "Erreur lors de l'inscription");
        }

        setIsLoading(false);
    };

    return (
        <Card className="w-full max-w-md glass-card hover-glow">
            <CardHeader className="text-center">
                <CardTitle className="text-xl">Créer un compte</CardTitle>
                <CardDescription>
                    Inscrivez-vous pour commencer à transcrire vos réunions
                </CardDescription>
            </CardHeader>

            <form onSubmit={handleSubmit}>
                <CardContent className="space-y-4">
                    {/* Full Name */}
                    <div className="space-y-2">
                        <Label htmlFor="fullName">Nom complet (optionnel)</Label>
                        <Input
                            id="fullName"
                            type="text"
                            placeholder="Jean Dupont"
                            value={fullName}
                            onChange={(e) => setFullName(e.target.value)}
                            autoComplete="name"
                            disabled={isLoading}
                        />
                    </div>

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
                                placeholder="8 caractères minimum"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                                minLength={8}
                                autoComplete="new-password"
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

                    {/* Confirm Password */}
                    <div className="space-y-2">
                        <Label htmlFor="confirmPassword">Confirmer le mot de passe</Label>
                        <Input
                            id="confirmPassword"
                            type={showPassword ? "text" : "password"}
                            placeholder="Répétez le mot de passe"
                            value={confirmPassword}
                            onChange={(e) => setConfirmPassword(e.target.value)}
                            required
                            autoComplete="new-password"
                            disabled={isLoading}
                        />
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
                                Création en cours...
                            </>
                        ) : (
                            <>
                                <UserPlus className="h-4 w-4" />
                                Créer mon compte
                            </>
                        )}
                    </Button>

                    <p className="text-sm text-text-secondary text-center">
                        Déjà un compte ?{" "}
                        <Link
                            href="/login"
                            className="text-accent-primary hover:underline font-medium"
                        >
                            Se connecter
                        </Link>
                    </p>
                </CardFooter>
            </form>
        </Card>
    );
}
