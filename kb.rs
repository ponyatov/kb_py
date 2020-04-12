// kb: Knowledge Base engine in Rust
// (c) Dmitry Ponyatov <<dponyatov@gmail.com>> 2020 MIT
// github: https://github.com/ponyatov/kb

use std::env;

fn main() {
    let argc: usize = env::args().count();
    assert!(argc > 1);
    let argv: Vec<String> = env::args().collect();
    let mut argi = 0;
    for arg in argv {
        println!("argv[{:?}] = {:?}", argi, arg);
        argi += 1;
    }
}
